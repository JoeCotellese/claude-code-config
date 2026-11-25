# ABOUTME: Reads Claude Code transcripts read-only: picks project dirs in scope, parses and validates records.
# ABOUTME: Yields ordered events per file (usage turns, skills, spawns, filings, /clear, DOD verdicts).
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
COMMAND_NAME_RE = re.compile(r"<command-name>/?([^<]*)</command-name>")
COMMAND_ARGS_RE = re.compile(r"<command-args>(.*?)</command-args>", re.S)
ISSUE_URL_RE = re.compile(r"github\.com/([^/\s]+/[^/\s]+)/issues/(\d+)")
BARE_ISSUE_URL_RE = re.compile(r"/issues/(\d+)")
VERDICT_RE = re.compile(r"^\W{0,3}DOD VERDICT: #(\d+)\b", re.M)
OBSERVER_MARKERS = ("claude-mem", "observer")


class TranscriptFormatError(Exception):
    """A record the parser cannot read without guessing. Carries the file and 1-based line."""

    def __init__(self, path, line: int, reason: str):
        super().__init__(f"{path}:{line}: {reason}")
        self.path = str(path)
        self.line = line
        self.reason = reason


# --- events ---------------------------------------------------------------
@dataclass
class Turn:
    path: str
    line: int
    ts: str
    model: str
    kind: str  # "message" for the executor's own call, "advisor_message" for an advisor call
    tokens: dict  # the five weights.CLASSES keys
    key: tuple

    @property
    def context(self) -> int:
        t = self.tokens
        return t["input"] + t["cache_read"] + t["cache_write_5m"] + t["cache_write_1h"]


@dataclass
class SkillCall:
    line: int
    ts: str
    skill: str
    args: str
    branch: str
    source: str  # "tool" or "command"


@dataclass
class Clear:
    line: int
    ts: str


@dataclass
class Filing:
    line: int
    ts: str
    refs: list  # [(owner/repo or None, issue number)]


@dataclass
class Spawn:
    line: int
    ts: str
    tool_use_id: str
    description: str


@dataclass
class Verdict:
    line: int
    ts: str
    issue: int


@dataclass
class FileTranscript:
    path: str
    events: list = field(default_factory=list)
    first_ts: str = ""
    last_ts: str = ""
    cwd: str | None = None

    @property
    def turns(self):
        return [e for e in self.events if isinstance(e, Turn)]


@dataclass
class Agent:
    agent_id: str
    agent_type: str
    description: str
    tool_use_id: str | None
    transcript: FileTranscript


@dataclass
class Session:
    sid: str
    project_dir: str
    main: FileTranscript
    agents: list


# --- scope ----------------------------------------------------------------
@dataclass
class Scope:
    """Which project dirs count as this repo's (decision 13)."""

    everything: bool = False
    worktrees: tuple = ()
    main_root: str | None = None
    globs: tuple = ()

    @classmethod
    def all_dirs(cls) -> "Scope":
        return cls(everything=True)

    @classmethod
    def for_repo(cls, repo, globs=()) -> "Scope":
        worktrees = git_worktrees(repo)
        return cls(worktrees=tuple(worktrees), main_root=worktrees[0] if worktrees else None,
                   globs=tuple(globs))

    def includes(self, cwd: str | None) -> bool:
        if self.everything:
            return True
        if not cwd:
            return False
        for tree in self.worktrees:
            if cwd == tree or cwd.startswith(tree.rstrip("/") + "/"):
                return True
        if self.main_root and not os.path.exists(cwd):
            if cwd.startswith(self.main_root + "-") or cwd.startswith(self.main_root + "/"):
                return True
        return any(fnmatch.fnmatch(cwd, g) for g in self.globs)


def git_worktrees(repo) -> list:
    try:
        out = subprocess.run(["git", "-C", str(repo), "worktree", "list", "--porcelain"],
                             capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    return [line[len("worktree "):] for line in out.stdout.splitlines() if line.startswith("worktree ")]


def is_observer(project_dir) -> bool:
    name = Path(project_dir).name
    return any(marker in name for marker in OBSERVER_MARKERS)


def project_cwd(project_dir) -> str | None:
    """The cwd of the first record carrying one, across the dir's main transcripts."""
    for path in sorted(Path(project_dir).glob("*.jsonl")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if '"cwd"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict) and isinstance(record.get("cwd"), str):
                    return record["cwd"]
    return None


def discover(projects_dir, scope: Scope):
    """Return (in-scope project dirs, observer dirs)."""
    projects_dir = Path(projects_dir)
    if not projects_dir.is_dir():
        return [], []
    in_scope, observers = [], []
    for child in sorted(projects_dir.iterdir()):
        if not child.is_dir():
            continue
        if is_observer(child):
            observers.append(child)
        elif scope.includes(project_cwd(child)):
            in_scope.append(child)
    return in_scope, observers


# --- sessions -------------------------------------------------------------
def mentions_issue(text: str, n: int) -> bool:
    return re.search(rf"(?<!\d){n}(?!\d)", text) is not None


def _file_mentions(path, n: int) -> bool:
    return mentions_issue(Path(path).read_text(encoding="utf-8", errors="replace"), n)


def session_files(project_dir):
    """Yield (sid, main path, [(meta dict, agent path)]) for every main transcript in a project dir."""
    for main in sorted(Path(project_dir).glob("*.jsonl")):
        sid = main.stem
        agents = []
        sub_dir = main.parent / sid / "subagents"
        if sub_dir.is_dir():
            for agent_path in sorted(sub_dir.glob("agent-*.jsonl")):
                meta_path = agent_path.with_name(agent_path.stem + ".meta.json")
                meta = {}
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text())
                    except ValueError:
                        meta = {}
                agents.append((meta, agent_path))
        yield sid, main, agents


def load_session(project_dir, sid: str, main, agents) -> Session:
    main_t = parse(main)
    agent_list = []
    for meta, path in agents:
        agent_list.append(Agent(
            agent_id=path.stem[len("agent-"):],
            agent_type=str(meta.get("agentType") or "agent"),
            description=str(meta.get("description") or ""),
            tool_use_id=meta.get("toolUseId"),
            transcript=parse(path),
        ))
    return Session(sid=sid, project_dir=str(project_dir), main=main_t, agents=agent_list)


def collect_sessions(project_dirs, issue: int | None = None):
    """Parse every session in the dirs; with an issue, only those whose text or agents mention it."""
    sessions = []
    for project_dir in project_dirs:
        for sid, main, agents in session_files(project_dir):
            if issue is not None:
                if not (_file_mentions(main, issue)
                        or any(mentions_issue(str(meta.get("description", "")), issue) for meta, _ in agents)
                        or any(_file_mentions(path, issue) for _, path in agents)):
                    continue
            sessions.append(load_session(project_dir, sid, main, agents))
    dedupe(sessions)
    return sessions


def find_session(projects_dir, sid: str):
    for main in Path(projects_dir).glob(f"*/{sid}.jsonl"):
        for found_sid, found_main, agents in session_files(main.parent):
            if found_sid == sid:
                session = load_session(main.parent, sid, found_main, agents)
                dedupe([session])
                return session
    return None


def dedupe(sessions) -> None:
    """Drop repeated usage turns globally on (message.id, requestId), earliest file first."""
    files = []
    for session in sessions:
        files.append(session.main)
        files.extend(agent.transcript for agent in session.agents)
    files.sort(key=lambda f: f.first_ts or "")
    seen = set()
    for transcript in files:
        kept = []
        for event in transcript.events:
            if isinstance(event, Turn):
                if event.key in seen:
                    continue
                seen.add(event.key)
            kept.append(event)
        transcript.events = kept


# --- parsing --------------------------------------------------------------
def parse(path) -> FileTranscript:
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    transcript = FileTranscript(path=str(path))
    pending_filings = {}
    seen_tools = set()
    seen_verdicts = set()
    last_index = len(lines)
    if content.endswith("\n"):
        lines = lines[:-1]
        last_index = None
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            if number == last_index:
                continue  # a live write still in progress
            raise TranscriptFormatError(path, number, "invalid JSON")
        if not isinstance(record, dict):
            raise TranscriptFormatError(path, number, "record is not a JSON object")
        ts = record.get("timestamp")
        if isinstance(ts, str):
            transcript.first_ts = transcript.first_ts or ts
            transcript.last_ts = ts
        else:
            ts = transcript.last_ts
        if transcript.cwd is None and isinstance(record.get("cwd"), str):
            transcript.cwd = record["cwd"]
        kind = record.get("type")
        if kind == "assistant":
            _parse_assistant(path, number, ts, record, transcript, pending_filings, seen_tools, seen_verdicts)
        elif kind == "user":
            _parse_user(number, ts, record, transcript, pending_filings)
    return transcript


def _parse_assistant(path, number, ts, record, transcript, pending_filings, seen_tools, seen_verdicts):
    message = record.get("message")
    if not isinstance(message, dict):
        raise TranscriptFormatError(path, number, "assistant record without a message object")
    model = message.get("model")
    if model == "<synthetic>":
        return
    for name, value in (("message.id", message.get("id")), ("requestId", record.get("requestId")),
                        ("message.model", model)):
        if not isinstance(value, str) or not value:
            raise TranscriptFormatError(path, number, f"assistant record missing {name}")
    usage = message.get("usage")
    if not isinstance(usage, dict):
        raise TranscriptFormatError(path, number, "assistant record missing message.usage")
    _check_usage(path, number, usage, "message.usage")
    branch = record.get("gitBranch") or ""
    content = message.get("content")
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            tool_id = block.get("id")
            if tool_id in seen_tools:
                continue
            seen_tools.add(tool_id)
            _parse_tool_use(number, ts, branch, block, transcript, pending_filings)
        elif block.get("type") == "text":
            for match in VERDICT_RE.finditer(block.get("text") or ""):
                key = (message["id"], int(match.group(1)))
                if key not in seen_verdicts:
                    seen_verdicts.add(key)
                    transcript.events.append(Verdict(number, ts, int(match.group(1))))
    key_base = (message["id"], record["requestId"])
    iterations = usage.get("iterations")
    if isinstance(iterations, list) and iterations:
        for index, it in enumerate(iterations):
            if not isinstance(it, dict):
                raise TranscriptFormatError(path, number, f"usage.iterations[{index}] is not an object")
            _check_usage(path, number, it, f"usage.iterations[{index}]")
            transcript.events.append(Turn(
                str(path), number, ts, str(it.get("model") or model), str(it.get("type") or "message"),
                _tokens(it), key_base + (index,)))
    else:
        transcript.events.append(Turn(str(path), number, ts, str(model), "message", _tokens(usage),
                                     key_base + (0,)))


def _check_usage(path, number, usage, where):
    for name in USAGE_FIELDS:
        value = usage.get(name)
        if not isinstance(value, int) or isinstance(value, bool):
            raise TranscriptFormatError(path, number, f"{where} missing integer {name}")


def _tokens(usage) -> dict:
    creation = usage.get("cache_creation") if isinstance(usage.get("cache_creation"), dict) else {}
    one_hour = creation.get("ephemeral_1h_input_tokens") or 0
    total_writes = usage["cache_creation_input_tokens"]
    return {
        "input": usage["input_tokens"],
        "output": usage["output_tokens"],
        "cache_read": usage["cache_read_input_tokens"],
        "cache_write_5m": total_writes - one_hour,
        "cache_write_1h": one_hour,
    }


def _parse_tool_use(number, ts, branch, block, transcript, pending_filings):
    name = block.get("name")
    data = block.get("input") if isinstance(block.get("input"), dict) else {}
    if name == "Skill":
        transcript.events.append(SkillCall(number, ts, str(data.get("skill") or ""),
                                           str(data.get("args") or ""), branch, "tool"))
    elif name in ("Agent", "Task"):
        transcript.events.append(Spawn(number, ts, str(block.get("id")), str(data.get("description") or "")))
    elif name == "Bash" and "gh issue create" in str(data.get("command") or ""):
        pending_filings[block.get("id")] = True


def _parse_user(number, ts, record, transcript, pending_filings):
    message = record.get("message")
    if not isinstance(message, dict):
        return
    content = message.get("content")
    branch = record.get("gitBranch") or ""
    if isinstance(content, str):
        _parse_command(number, ts, branch, content, transcript)
        return
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            _parse_command(number, ts, branch, block.get("text") or "", transcript)
        elif block.get("type") == "tool_result" and pending_filings.pop(block.get("tool_use_id"), False):
            text = _result_text(block.get("content"))
            refs = [(repo, int(n)) for repo, n in ISSUE_URL_RE.findall(text)]
            if not refs:
                refs = [(None, int(n)) for n in BARE_ISSUE_URL_RE.findall(text)]
            if refs:
                transcript.events.append(Filing(number, ts, refs))


def _parse_command(number, ts, branch, text, transcript):
    match = COMMAND_NAME_RE.search(text)
    if not match:
        return
    name = match.group(1).strip()
    args_match = COMMAND_ARGS_RE.search(text)
    args = args_match.group(1).strip() if args_match else ""
    if name == "clear":
        transcript.events.append(Clear(number, ts))
    else:
        transcript.events.append(SkillCall(number, ts, name, args, branch, "command"))


def _result_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(b.get("text") or "") for b in content if isinstance(b, dict))
    return ""
