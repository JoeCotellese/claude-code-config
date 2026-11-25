# ABOUTME: /cost entry point: per-issue or per-session weighted-token report from Claude Code transcripts.
# ABOUTME: Also writes the per-issue snapshot (--snapshot) and the one-line summary (--summary).
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import attribution
import outcome
import report
import transcripts
import weights
from transcripts import Scope, TranscriptFormatError

__all__ = ["Scope", "issue_report", "session_report", "main"]

DEFAULT_PROJECTS = Path.home() / ".claude" / "projects"


# --- public API -----------------------------------------------------------
def issue_report(n: int, projects_dir, scope: Scope, github=None, origin: str | None = None,
                 repo: str | None = None):
    """The issue view for #n, or None when no in-scope transcript is attributed to it."""
    dirs, _ = transcripts.discover(projects_dir, scope)
    sessions = transcripts.collect_sessions(dirs, issue=n)
    attributed = attribution.attribute(sessions, origin)
    return report.build_issue_report(n, attributed, github, repo or origin)


def session_report(session_id: str, projects_dir, origin: str | None = None):
    """The session view: one row per issue the session touched, plus unattributed."""
    session = transcripts.find_session(projects_dir, session_id)
    if session is None:
        return None
    attributed = attribution.attribute([session], origin)
    return report.build_session_report(session_id, attributed, _background(projects_dir, session))


def _background(projects_dir, session) -> Fraction:
    files = [session.main] + [a.transcript for a in session.agents]
    start = min((f.first_ts for f in files if f.first_ts), default="")
    end = max((f.last_ts for f in files if f.last_ts), default="")
    if not start:
        return Fraction(0)
    _, observers = transcripts.discover(projects_dir, Scope.all_dirs())
    total = Fraction(0)
    for project_dir in observers:
        for path in Path(project_dir).rglob("*.jsonl"):
            for turn in transcripts.parse(path).turns:
                if start <= turn.ts <= end:
                    total += weights.weigh(turn.model, turn.tokens)
    return total


# --- CLI ------------------------------------------------------------------
def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cost", description="Token pressure per dev-jawn issue or session.")
    p.add_argument("issue", nargs="?", help="#N for the issue view; omit for the current session")
    p.add_argument("--snapshot", action="store_true", help="write .dev-jawn/cost/<N>.json and print the summary")
    p.add_argument("--summary", action="store_true", help="print the one-line summary only")
    p.add_argument("--session-id", default=None, help="session for the no-argument view")
    p.add_argument("--repo", default=None, help="repository the issue belongs to (default: cwd)")
    p.add_argument("--projects-dir", default=str(DEFAULT_PROJECTS), help="Claude Code transcripts root")
    p.add_argument("--project", action="append", default=[], help="extra cwd glob to treat as this repo")
    p.add_argument("--offline", action="store_true", help="skip the gh outcome lookup")
    return p


def _git(repo, *argv) -> str | None:
    try:
        done = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def origin_repo(repo) -> str | None:
    url = _git(repo, "remote", "get-url", "origin")
    match = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url or "")
    return match.group(1) if match else None


def main(argv=None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.issue:
            digits = args.issue.lstrip("#")
            if not digits.isdigit():
                parser.error(f"issue must look like #N, got {args.issue!r}")
            out = _issue_command(int(digits), args)
        else:
            out = _session_command(args)
    except TranscriptFormatError as error:
        print(f"cost: {error.path}:{error.line}: {error.reason}", file=sys.stderr)
        return 1
    sys.stdout.write(out)
    return 0


def _issue_command(n: int, args) -> str:
    repo = Path(args.repo or os.getcwd())
    toplevel = Path(_git(repo, "rev-parse", "--show-toplevel") or repo)
    origin = origin_repo(repo)
    lookup_failed = []

    def github(issue):
        state = outcome.lookup(issue, cwd=str(repo))
        if state is None:
            lookup_failed.append(issue)
        return state

    gh = None if args.offline else github
    scope = Scope.for_repo(repo, args.project)
    live = issue_report(n, args.projects_dir, scope, gh, origin)
    snapshot = report.read_snapshot(toplevel, n)

    if args.snapshot:
        if live is None:
            return f"#{n}: nothing found (no sessions in scope); no snapshot written\n"
        report.write_snapshot(live, toplevel)
        _warn_outcome(args.offline, lookup_failed)
        return report.summary_line(live) + "\n"

    chosen = live
    if snapshot and (live is None or _snapshot_sessions_gone(args.projects_dir, snapshot)):
        state = None if args.offline else github(n)
        chosen = report.report_from_snapshot(snapshot, outcome.outcome(state) if state else None)
    _warn_outcome(args.offline, lookup_failed)
    if chosen is None:
        return f"#{n}: nothing found (no sessions in scope and no snapshot)\n"
    if args.summary:
        return report.summary_line(chosen) + "\n"
    return report.render(report.issue_table(chosen))


def _warn_outcome(offline: bool, failed: list) -> None:
    if offline:
        print("cost: offline; outcome unknown", file=sys.stderr)
    elif failed:
        print("cost: gh lookup failed; outcome unknown", file=sys.stderr)


def _snapshot_sessions_gone(projects_dir, snapshot: dict) -> bool:
    root = Path(projects_dir)
    return any(not list(root.glob(f"*/{sid}.jsonl")) for sid in snapshot.get("sessions", []))


def _session_command(args) -> str:
    sid = args.session_id or _newest_session(args.projects_dir)
    if not sid:
        return "cost: no session found for this directory\n"
    result = session_report(sid, args.projects_dir, origin_repo(Path(os.getcwd())))
    if result is None:
        return f"cost: session {sid} not found under {args.projects_dir}\n"
    return report.render(report.session_table(result))


def _newest_session(projects_dir) -> str | None:
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    mains = sorted(Path(projects_dir, slug).glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return mains[-1].stem if mains else None


if __name__ == "__main__":
    sys.exit(main())
