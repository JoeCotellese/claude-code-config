# ABOUTME: Aggregates attributed turns into /cost issue and session reports, renders them as text tables.
# ABOUTME: Also writes and reads the per-issue snapshot committed at .dev-jawn/cost/<N>.json.
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import weights
from attribution import PHASES
from outcome import outcome

CONTEXT_LIMIT = 200_000
SNAPSHOT_SCHEMA = 1


@dataclass
class PhaseRow:
    phase: str
    attempts: int = 0
    weighted: Fraction = Fraction(0)
    main: Fraction = Fraction(0)
    subagent: Fraction = Fraction(0)
    shared: Fraction = Fraction(0)
    advisor: Fraction = Fraction(0)
    over_200k: Fraction = Fraction(0)
    peak_context: int = 0
    models: dict = field(default_factory=dict)

    @property
    def rework(self) -> bool:
        return self.attempts >= 2

    @property
    def share_over_200k(self) -> Fraction:
        return self.over_200k / self.weighted if self.weighted else Fraction(0)


@dataclass
class Totals:
    weighted: Fraction = Fraction(0)
    main: Fraction = Fraction(0)
    subagent: Fraction = Fraction(0)
    advisor: Fraction = Fraction(0)
    over_200k: Fraction = Fraction(0)
    peak_context: int = 0


@dataclass
class Pressure:
    agent: str
    over_200k: Fraction
    peak_context: int


@dataclass
class IssueReport:
    issue: int
    phases: list
    totals: Totals
    models: dict
    top_pressure: Pressure | None
    highest_peak: Pressure | None
    outcome: str
    dod_rounds: int
    sessions: list
    warnings: list
    first_activity: str | None
    last_activity: str | None
    source: str = "transcripts"
    snapshot_time: str | None = None
    repo: str | None = None


@dataclass
class SessionReport:
    session: str
    rows: list  # [(label, weighted)] issues in first-seen order, then unattributed
    total: Fraction
    background: Fraction
    top_pressure: Pressure | None
    highest_peak: Pressure | None
    warnings: list


@dataclass
class Table:
    columns: list
    rows: list
    notes: list = field(default_factory=list)


# --- building -------------------------------------------------------------
def _weighted(at) -> Fraction:
    return weights.weigh(at.turn.model, at.turn.tokens) * at.share


def _warnings(turns) -> list:
    unknown = sorted({t.turn.model for t in turns if not weights.is_known(t.turn.model)})
    return [f"unknown model {m}: counted at {weights.OPUS} weights" for m in unknown]


def _pressure(turns):
    agents = {}
    for at in turns:
        label, over, peak = agents.get(at.agent_key, (at.agent, Fraction(0), 0))
        if at.turn.context > CONTEXT_LIMIT:
            over += _weighted(at)
        agents[at.agent_key] = (label, over, max(peak, at.turn.context))
    top = None
    highest = None
    for label, over, peak in agents.values():
        if over > 0 and (top is None or over > top.over_200k):
            top = Pressure(label, over, peak)
        if highest is None or peak > highest.peak_context:
            highest = Pressure(label, over, peak)
    return top, highest


def build_issue_report(n: int, attribution, github=None, repo: str | None = None) -> IssueReport | None:
    """Report for issue n over already-attributed turns. None when nothing is attributed to n."""
    turns = [at for at in attribution.turns if n in at.issues]
    attempts = {phase: count for (issue, phase), count in attribution.attempts.items() if issue == n}
    if not turns and not attempts:
        return None
    rows = {phase: PhaseRow(phase, attempts=attempts.get(phase, 0)) for phase in PHASES}
    totals = Totals()
    models = {}
    for at in turns:
        w = _weighted(at)
        row = rows[at.slot.phase if at.slot.phase in rows else "other"]
        context = at.turn.context
        for bucket in (row, totals):
            bucket.weighted += w
            if at.is_main:
                bucket.main += w
            else:
                bucket.subagent += w
            if at.turn.kind == "advisor_message":
                bucket.advisor += w
            if context > CONTEXT_LIMIT:
                bucket.over_200k += w
            bucket.peak_context = max(bucket.peak_context, context)
        if at.shared:
            row.shared += w
        model = weights.normalize_model(at.turn.model)
        row.models[model] = row.models.get(model, Fraction(0)) + w
        entry = models.setdefault(model, {"weighted": Fraction(0), **{c: Fraction(0) for c in weights.CLASSES}})
        entry["weighted"] += w
        for c in weights.CLASSES:
            entry[c] += at.turn.tokens[c] * at.share
    top, highest = _pressure(turns)
    stamps = sorted(at.turn.ts for at in turns if at.turn.ts)
    state = github(n) if github else None
    return IssueReport(
        issue=n,
        phases=[r for r in rows.values() if r.weighted or r.attempts],
        totals=totals,
        models=models,
        top_pressure=top,
        highest_peak=highest,
        outcome=outcome(state),
        dod_rounds=attribution.verdicts.get(n, 0),
        sessions=sorted({at.session for at in turns}),
        warnings=_warnings(turns),
        first_activity=stamps[0] if stamps else None,
        last_activity=stamps[-1] if stamps else None,
        repo=repo,
    )


def build_session_report(session_id: str, attribution, background: Fraction = Fraction(0)) -> SessionReport:
    turns = [at for at in attribution.turns if at.session == session_id]
    issues = {}
    unattributed = Fraction(0)
    total = Fraction(0)
    for at in turns:
        full = weights.weigh(at.turn.model, at.turn.tokens)
        total += full
        if not at.issues:
            unattributed += full
        for n in at.issues:
            issues[n] = issues.get(n, Fraction(0)) + full * at.share
    rows = [(f"#{n}", w) for n, w in issues.items()] + [("unattributed", unattributed)]
    top, highest = _pressure(turns)
    return SessionReport(session_id, rows, total, background, top, highest, _warnings(turns))


# --- rendering ------------------------------------------------------------
def _n(value) -> str:
    return f"{round(value):,}"


def _pct(value: Fraction) -> str:
    return f"{float(value) * 100:.0f}%"


def _pressure_line(top, highest) -> str:
    if top:
        return f"top pressure: {top.agent} ({_n(top.over_200k)} weighted over 200K, peak {_n(top.peak_context)})"
    if highest:
        return f"top pressure: no agent over 200K; highest peak {highest.agent} (peak {_n(highest.peak_context)})"
    return "top pressure: none"


def issue_table(report: IssueReport) -> Table:
    columns = ["phase", "weighted", "main", "subagent", "advisor", "shared", "attempts",
               "peak ctx", "over 200K", "models"]
    rows = []
    for r in report.phases:
        models = ", ".join(f"{m} {_n(w)}" for m, w in sorted(r.models.items(), key=lambda kv: -kv[1]))
        rows.append([r.phase, _n(r.weighted), _n(r.main), _n(r.subagent), _n(r.advisor), _n(r.shared),
                     str(r.attempts), _n(r.peak_context), _pct(r.share_over_200k), models])
    t = report.totals
    rows.append(["total", _n(t.weighted), _n(t.main), _n(t.subagent), _n(t.advisor), "", "",
                 _n(t.peak_context), _pct(t.over_200k / t.weighted if t.weighted else Fraction(0)), ""])
    if report.source == "snapshot":
        notes = [f"#{report.issue}: from the committed snapshot taken {report.snapshot_time} "
                 f"(transcripts no longer on disk)"]
    else:
        notes = [f"#{report.issue}: from {len(report.sessions)} session(s) of transcripts"]
    notes.append(f"outcome: {report.outcome}; /dod rounds: {report.dod_rounds}")
    notes.append(_pressure_line(report.top_pressure, report.highest_peak))
    for r in report.phases:
        if r.rework:
            notes.append(f"rework: {r.phase} ran {r.attempts} times")
    notes.extend(f"warning: {w}" for w in report.warnings)
    return Table(columns, rows, notes)


def session_table(report: SessionReport) -> Table:
    rows = [[label, _n(w)] for label, w in report.rows]
    rows.append(["total", _n(report.total)])
    notes = [f"session {report.session[:8]}",
             _pressure_line(report.top_pressure, report.highest_peak)]
    if report.highest_peak:
        notes.append(f"highest peak: {report.highest_peak.agent} (peak {_n(report.highest_peak.peak_context)})")
    notes.append(f"background (claude-mem observer, outside the total): {_n(report.background)}")
    notes.extend(f"warning: {w}" for w in report.warnings)
    return Table(["issue", "weighted"], rows, notes)


def render(table: Table) -> str:
    widths = [len(c) for c in table.columns]
    for row in table.rows:
        widths = [max(w, len(cell)) for w, cell in zip(widths, row)]

    def line(cells):
        out = []
        for i, (cell, width) in enumerate(zip(cells, widths)):
            out.append(cell.ljust(width) if i == 0 or i == len(cells) - 1 else cell.rjust(width))
        return "  ".join(out).rstrip()

    lines = [table.notes[0]] if table.notes else []
    lines.append(line(table.columns))
    lines.extend(line(row) for row in table.rows)
    lines.extend(table.notes[1:])
    return "\n".join(lines) + "\n"


def summary_line(report: IssueReport) -> str:
    top = report.top_pressure or report.highest_peak
    tail = f"; top pressure {top.agent} (peak {_n(top.peak_context)})" if top else ""
    return f"#{report.issue}: {_n(report.totals.weighted)} weighted tokens{tail}"


# --- snapshot -------------------------------------------------------------
def plugin_version() -> str | None:
    manifest = Path(__file__).resolve().parents[2] / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text()).get("version")
    except (OSError, ValueError):
        return None


def _exact(value: Fraction):
    return int(value) if value.denominator == 1 else round(float(value), 3)


def snapshot_dict(report: IssueReport, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    t = report.totals
    top = report.top_pressure
    return {
        "schema": SNAPSHOT_SCHEMA,
        "issue": report.issue,
        "repo": report.repo,
        "snapshot_time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plugin_version": plugin_version(),
        "weight_table": weights.WEIGHT_TABLE_DATE,
        "outcome": report.outcome,
        "dod_rounds": report.dod_rounds,
        "sessions": report.sessions,
        "first_activity": report.first_activity,
        "last_activity": report.last_activity,
        "totals": {"weighted": round(t.weighted), "main": round(t.main), "subagent": round(t.subagent),
                   "advisor": round(t.advisor), "over_200k": round(t.over_200k), "peak_context": t.peak_context},
        "phases": [{
            "phase": r.phase, "attempts": r.attempts, "rework": r.rework, "weighted": round(r.weighted),
            "main": round(r.main), "subagent": round(r.subagent), "shared": round(r.shared),
            "advisor": round(r.advisor), "peak_context": r.peak_context,
            "share_over_200k": round(float(r.share_over_200k), 3),
            "models": {m: round(w) for m, w in r.models.items()},
        } for r in report.phases],
        "models": {m: {k: (round(v) if k == "weighted" else _exact(v)) for k, v in entry.items()}
                   for m, entry in report.models.items()},
        "top_pressure": ({"agent": top.agent, "over_200k": round(top.over_200k), "peak_context": top.peak_context}
                         if top else None),
        "warnings": report.warnings,
    }


def snapshot_path(repo_root, n: int) -> Path:
    return Path(repo_root) / ".dev-jawn" / "cost" / f"{n}.json"


def write_snapshot(report: IssueReport, repo_root) -> Path:
    path = snapshot_path(repo_root, report.issue)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot_dict(report), indent=2) + "\n")
    return path


def read_snapshot(repo_root, n: int) -> dict | None:
    path = snapshot_path(repo_root, n)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def report_from_snapshot(data: dict, outcome_value: str | None = None) -> IssueReport:
    F = Fraction
    phases = []
    for p in data.get("phases", []):
        row = PhaseRow(p["phase"], attempts=p.get("attempts", 0), weighted=F(p.get("weighted", 0)),
                       main=F(p.get("main", 0)), subagent=F(p.get("subagent", 0)), shared=F(p.get("shared", 0)),
                       advisor=F(p.get("advisor", 0)), peak_context=p.get("peak_context", 0),
                       models={m: F(w) for m, w in (p.get("models") or {}).items()})
        row.over_200k = F(str(p.get("share_over_200k", 0))) * row.weighted
        phases.append(row)
    t = data.get("totals", {})
    totals = Totals(F(t.get("weighted", 0)), F(t.get("main", 0)), F(t.get("subagent", 0)),
                    F(t.get("advisor", 0)), F(t.get("over_200k", 0)), t.get("peak_context", 0))
    top = data.get("top_pressure")
    return IssueReport(
        issue=data["issue"], phases=phases, totals=totals, models=data.get("models", {}),
        top_pressure=Pressure(top["agent"], F(top["over_200k"]), top["peak_context"]) if top else None,
        highest_peak=None, outcome=outcome_value or data.get("outcome", "unknown"),
        dod_rounds=data.get("dod_rounds", 0), sessions=data.get("sessions", []),
        warnings=data.get("warnings", []), first_activity=data.get("first_activity"),
        last_activity=data.get("last_activity"), source="snapshot",
        snapshot_time=data.get("snapshot_time"), repo=data.get("repo"),
    )
