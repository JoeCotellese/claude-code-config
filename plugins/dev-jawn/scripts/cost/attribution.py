# ABOUTME: Binds every usage turn to an issue (or unattributed) and a phase, from the transcripts' own signals.
# ABOUTME: Walks main sessions then subagents parent-first; counts phase attempts and /dod verdict rounds.
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction

from transcripts import Clear, Filing, Session, SkillCall, Spawn, Turn, Verdict

PHASES = ("spec", "ui-design", "ready", "architecture", "build", "dod", "submit", "other")
SKILL_PHASE = {
    "dev-jawn:spec": "spec",
    "dev-jawn:ui-design": "ui-design",
    "dev-jawn:ready": "ready",
    "dev-jawn:architecture": "architecture",
    "dev-jawn:implement": "build",
    "dev-jawn:dod": "dod",
    "dev-jawn:submit": "submit",
    "dev-jawn:retro": "other",
    "dev-jawn:autopilot": "other",
}
AUTOPILOT = "dev-jawn:autopilot"
AGENT_TYPE_PHASE = {
    "dev-jawn:architect": "architecture",
    "dev-jawn:acceptance-criteria-reviewer": "submit",
    "dev-jawn:test-adequacy-reviewer": "submit",
    "swift-swiftui-reviewer": "submit",
    "python-code-reviewer": "submit",
    "cpp-qt-reviewer": "submit",
}
DESCRIPTION_PHASE = [
    (re.compile(r"^(build|implement)", re.I), "build"),
    (re.compile(r"^architect", re.I), "architecture"),
    (re.compile(r"^spec(\b|s\b|ification)", re.I), "spec"),
    (re.compile(r"^(lens|review|/code-review|code review)", re.I), "submit"),
    (re.compile(r"^(dod\b|definition of done)", re.I), "dod"),
    (re.compile(r"^(ready\b|dor\b)", re.I), "ready"),
    (re.compile(r"^(critic|design critic|prototype)", re.I), "ui-design"),
]
ISSUE_RE = re.compile(r"#(\d+)")
BRANCH_RE = re.compile(r"^[a-z]+/(\d+)-")


@dataclass
class Slot:
    """Where a turn or spawn lands. Pending slots are filled when the segment binds."""

    issues: tuple = ()
    phase: str = "other"
    locked: bool = False


@dataclass
class AttributedTurn:
    turn: Turn
    slot: Slot
    agent: str
    agent_key: str
    is_main: bool
    session: str

    @property
    def issues(self) -> tuple:
        return self.slot.issues

    @property
    def share(self) -> Fraction:
        return Fraction(1, len(self.slot.issues)) if self.slot.issues else Fraction(1)

    @property
    def shared(self) -> bool:
        return len(self.slot.issues) > 1


@dataclass
class Attribution:
    turns: list = field(default_factory=list)
    attempts: Counter = field(default_factory=Counter)  # (issue, phase) -> entries
    verdicts: Counter = field(default_factory=Counter)  # issue -> DOD VERDICT rounds
    sessions: list = field(default_factory=list)


def phase_for_agent(agent_type: str, description: str):
    if agent_type in AGENT_TYPE_PHASE:
        return AGENT_TYPE_PHASE[agent_type]
    text = description.strip()
    for pattern, phase in DESCRIPTION_PHASE:
        if pattern.search(text):
            return phase
    return None


def description_issues(description: str) -> list:
    found = []
    for n in ISSUE_RE.findall(description):
        if int(n) not in found:
            found.append(int(n))
    return found


class Walker:
    """The binding and phase state machine for one transcript file (decision 15)."""

    def __init__(self, result: Attribution, origin: str | None, issues=(), phase=None, locked=False):
        self.result = result
        self.origin = origin.lower() if origin else None
        self.issues = tuple(issues)
        self.phase = phase
        self.locked = locked
        self.pending = []
        self.last_invocation = None
        self.turn_since_invocation = True
        self.spawn_slots = {}
        self.skill_slots = []  # (skill, args, ts, slot)
        self.timeline = []  # (ts, slot)

    def slot(self) -> Slot:
        if self.issues:
            return Slot(self.issues, self.phase or "other", self.locked)
        pending = Slot((), self.phase or "other", False)
        self.pending.append(pending)
        return pending

    def bind(self, issues: tuple, count_attempt: bool) -> None:
        first = not self.issues
        self.issues = issues
        for slot in self.pending:
            slot.issues = issues
            slot.phase = self.phase or "other"
        self.pending = []
        if count_attempt or first:
            for n in issues:
                self.result.attempts[(n, self.phase or "other")] += 1

    def close_segment(self) -> None:
        for slot in self.pending:
            slot.issues = ()
        self.pending = []

    def walk(self, transcript, on_turn) -> None:
        for event in transcript.events:
            if isinstance(event, Turn):
                slot = self.slot()
                self.timeline.append((event.ts, slot))
                self.turn_since_invocation = True
                on_turn(event, slot)
            elif isinstance(event, SkillCall):
                self.skill_slots.append((event.skill, event.args, event.ts, self.slot()))
                self.invoke(event)
            elif isinstance(event, Spawn):
                slot = self.slot()
                self.spawn_slots[event.tool_use_id] = slot
                self.timeline.append((event.ts, slot))
            elif isinstance(event, Filing):
                self.file(event)
            elif isinstance(event, Clear):
                self.close_segment()
                if not self.locked:
                    self.issues = ()
                self.phase = None
        self.close_segment()

    def invoke(self, call: SkillCall) -> None:
        if call.skill not in SKILL_PHASE:
            return
        signature = (call.skill, call.args)
        if signature == self.last_invocation and not self.turn_since_invocation:
            return  # the command record and its Skill tool_use are one invocation
        self.last_invocation = signature
        self.turn_since_invocation = False
        if call.skill == AUTOPILOT and self.phase is not None:
            return  # autopilot never overwrites a phase already set
        self.phase = SKILL_PHASE[call.skill]
        match = ISSUE_RE.search(call.args)
        n = int(match.group(1)) if match else None
        if n is None and not self.issues:
            branch = BRANCH_RE.match(call.branch or "")
            n = int(branch.group(1)) if branch else None
        if n is not None and not self.locked:
            self.bind((n,), count_attempt=True)
        elif self.issues:
            for issue in self.issues:
                self.result.attempts[(issue, self.phase)] += 1

    def file(self, filing: Filing) -> None:
        if self.phase is None or self.locked:
            return
        for repo, n in filing.refs:
            if self.origin and repo and repo.lower() != self.origin:
                continue
            self.bind((n,), count_attempt=self.issues != (n,))


def attribute(sessions, origin: str | None = None) -> Attribution:
    result = Attribution()
    for session in sessions:
        _attribute_session(session, result, origin)
    return result


def _attribute_session(session: Session, result: Attribution, origin) -> None:
    result.sessions.append(session.sid)
    collected = []

    def collector(label, key, is_main):
        def on_turn(turn, slot):
            collected.append(AttributedTurn(turn, slot, label, key, is_main, session.sid))
        return on_turn

    for transcript in [session.main] + [a.transcript for a in session.agents]:
        for event in transcript.events:
            if isinstance(event, Verdict):
                result.verdicts[event.issue] += 1

    main = Walker(result, origin)
    main.walk(session.main, collector(f"main session {session.sid[:8]}", session.main.path, True))
    spawn_slots = dict(main.spawn_slots)
    skill_slots = list(main.skill_slots)
    remaining = sorted(session.agents, key=lambda a: a.transcript.first_ts or "")
    while remaining:
        ready = [a for a in remaining if a.tool_use_id and a.tool_use_id in spawn_slots]
        if ready:
            agent = ready[0]
            parent = spawn_slots[agent.tool_use_id]
        else:
            agent = remaining[0]
            parent = _skill_link(agent, skill_slots) or _timeline_slot(main.timeline, agent.transcript.first_ts)
        remaining.remove(agent)
        walker = _agent_walker(agent, parent, result, origin)
        label = f'{agent.agent_type} "{agent.description}"'
        walker.walk(agent.transcript, collector(label, agent.transcript.path, False))
        spawn_slots.update(walker.spawn_slots)
        skill_slots.extend(walker.skill_slots)
    result.turns.extend(collected)


def _agent_walker(agent, parent: Slot, result: Attribution, origin) -> Walker:
    named = description_issues(agent.description)
    # One #N names this agent's issue even inside a shared pair ("Architect #1119" under "Spec
    # pair #1118 + #1119"); two or more lock an even split; none inherits, lock included.
    if len(named) == 1:
        issues, locked = (named[0],), False
    elif len(named) >= 2:
        issues, locked = tuple(named), True
    elif parent.locked:
        issues, locked = parent.issues, True
    else:
        issues, locked = parent.issues, False
    identity = phase_for_agent(agent.agent_type, agent.description)
    if identity and identity != parent.phase:
        for n in issues:
            result.attempts[(n, identity)] += 1
    return Walker(result, origin, issues=issues, phase=identity or parent.phase, locked=locked)


def _skill_link(agent, skill_slots):
    description = re.sub(r"(…|\.\.\.)$", "", agent.description.strip()).strip()
    if not description:
        return None
    match = None
    for skill, args, ts, slot in skill_slots:
        invocation = f"/{skill} {args}".strip()
        if invocation.startswith(description) and ts <= (agent.transcript.first_ts or ts):
            match = slot
    return match


def _timeline_slot(timeline, ts) -> Slot:
    chosen = Slot()
    for when, slot in timeline:
        if ts and when and when > ts:
            break
        chosen = slot
    return chosen
