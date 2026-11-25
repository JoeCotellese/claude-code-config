# ABOUTME: Looks up an issue's GitHub state with gh (injectable runner) for the /cost outcome line.
# ABOUTME: Maps the state to merged, stopped or open; any gh failure yields None, shown as unknown.
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass

TIMEOUT_SECONDS = 15


@dataclass
class GitHubState:
    merged: bool = False  # a pull request that closed the issue exists
    stage_human: bool = False  # the issue carries stage:human
    open_ready_pr: bool = False  # an open, non-draft PR closes the issue or sits on its branch


def outcome(state: GitHubState | None) -> str:
    if state is None:
        return "unknown"
    if state.merged:
        return "merged"
    if state.stage_human and not state.open_ready_pr:
        return "stopped"
    return "open"


def lookup(n: int, runner=subprocess.run, cwd=None) -> GitHubState | None:
    issue = _gh(runner, cwd, ["gh", "issue", "view", str(n), "--json", "labels,closedByPullRequestsReferences"])
    if issue is None:
        return None
    prs = _gh(runner, cwd, ["gh", "pr", "list", "--state", "open", "--search", str(n),
                            "--json", "number,isDraft,headRefName,closingIssuesReferences"])
    if prs is None:
        return None
    labels = {label.get("name") for label in issue.get("labels") or []}
    branch = re.compile(rf"^[a-z]+/{n}-")
    open_ready = False
    for pr in prs:
        closes = any(ref.get("number") == n for ref in pr.get("closingIssuesReferences") or [])
        if (closes or branch.match(pr.get("headRefName") or "")) and not pr.get("isDraft"):
            open_ready = True
    return GitHubState(
        merged=bool(issue.get("closedByPullRequestsReferences")),
        stage_human="stage:human" in labels,
        open_ready_pr=open_ready,
    )


def _gh(runner, cwd, argv):
    try:
        done = runner(argv, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, cwd=cwd)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    try:
        return json.loads(done.stdout)
    except ValueError:
        return None
