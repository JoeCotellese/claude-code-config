# ABOUTME: Builds small Claude Code transcript trees (main sessions, subagents, meta.json) for /cost tests.
# ABOUTME: Records mirror the real shapes in fixtures/record_shapes.jsonl; every usage turn is written twice.
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_TIME = datetime(2026, 11, 1, tzinfo=timezone.utc)


def slug_for(cwd: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", cwd)


class TranscriptTree:
    """A projects directory (stand-in for ~/.claude/projects) that tests fill with sessions."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._tick = 0
        self._ids = 0

    def now(self) -> str:
        self._tick += 1
        stamp = BASE_TIME + timedelta(seconds=self._tick)
        return stamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def next_id(self, prefix: str) -> str:
        self._ids += 1
        return f"{prefix}{self._ids:06d}"

    def session(self, sid: str, cwd: str = "/work/repo", branch: str = "main", slug: str | None = None):
        project = self.root / (slug or slug_for(cwd))
        project.mkdir(parents=True, exist_ok=True)
        return SessionWriter(self, project / f"{sid}.jsonl", sid, cwd, branch, agent_id=None)


class SessionWriter:
    """Appends records to one transcript file; subagent() opens a nested writer under <sid>/subagents/."""

    def __init__(self, tree: TranscriptTree, path: Path, sid: str, cwd: str, branch: str, agent_id):
        self.tree = tree
        self.path = path
        self.sid = sid
        self.cwd = cwd
        self.branch = branch
        self.agent_id = agent_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    # --- low level -------------------------------------------------------
    def _base(self, kind: str) -> dict:
        record = {
            "type": kind,
            "uuid": self.tree.next_id("uuid-"),
            "parentUuid": None,
            "timestamp": self.tree.now(),
            "sessionId": self.sid,
            "cwd": self.cwd,
            "gitBranch": self.branch,
            "isSidechain": self.agent_id is not None,
            "userType": "external",
            "version": "2.1.331",
        }
        if self.agent_id is not None:
            record["agentId"] = self.agent_id
        return record

    def _write(self, record: dict) -> None:
        with self.path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")

    def raw_line(self, text: str, newline: bool = True):
        with self.path.open("a") as handle:
            handle.write(text + ("\n" if newline else ""))
        return self

    def _assistant(self, content: list, model: str = "claude-opus-5-5", usage: dict | None = None,
                   copies: int = 1) -> None:
        record = self._base("assistant")
        record["requestId"] = self.tree.next_id("req_")
        record["message"] = {
            "id": self.tree.next_id("msg_"),
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": content,
            "usage": usage or _usage(0, 0, 0),
        }
        for _ in range(copies):
            self._write(record)

    def _user(self, content) -> None:
        record = self._base("user")
        record["message"] = {"role": "user", "content": content}
        self._write(record)

    # --- builder API ------------------------------------------------------
    def turn(self, model: str, input: int, output: int, cache_read: int, cw5m: int = 0, cw1h: int = 0,
             advisor: tuple | None = None, iterations: list | None = None):
        """One API turn, written twice with the same (message.id, requestId) so dedupe is exercised.

        advisor=(model, input, output) adds an advisor_message iteration the top-level usage omits.
        iterations=[(input, output, cache_read, cw5m, cw1h), ...] splits the turn into message
        iterations; the top-level usage is then their sum, as in real transcripts.
        """
        if iterations:
            parts = [_usage(i, o, r, w5, w1, kind="message") for (i, o, r, w5, w1) in iterations]
            s_in, s_out, s_read, s_5m, s_1h = (sum(it[i] for it in iterations) for i in range(5))
            usage = _usage(s_in, s_out, s_read, s_5m, s_1h)
        else:
            parts = [_usage(input, output, cache_read, cw5m, cw1h, kind="message")]
            usage = _usage(input, output, cache_read, cw5m, cw1h)
        if advisor:
            adv_model, adv_in, adv_out = advisor
            extra = _usage(adv_in, adv_out, 0, 0, 0, kind="advisor_message")
            extra["model"] = adv_model
            parts.append(extra)
        if advisor or iterations:
            usage["iterations"] = parts
        self._assistant([{"type": "text", "text": ""}], model=model, usage=usage, copies=2)
        return self

    def skill(self, name: str, args: str = ""):
        tool_id = self.tree.next_id("toolu_skill")
        self._assistant([{"type": "tool_use", "id": tool_id, "name": "Skill",
                          "input": {"skill": name, "args": args}}])
        return self

    def command(self, name: str, args: str = ""):
        self._user(f"<command-name>/{name}</command-name>\n"
                   f"            <command-message>{name}</command-message>\n"
                   f"            <command-args>{args}</command-args>")
        return self

    def clear(self):
        return self.command("clear")

    def filing(self, url: str):
        tool_id = self.tree.next_id("toolu_bash")
        self._assistant([{"type": "tool_use", "id": tool_id, "name": "Bash",
                          "input": {"command": "gh issue create --title t --body-file b.md"}}])
        self._user([{"type": "tool_result", "tool_use_id": tool_id, "content": url + "\n"}])
        return self

    def spawn(self, tool_use_id: str, description: str, subagent_type: str = "general-purpose"):
        self._assistant([{"type": "tool_use", "id": tool_use_id, "name": "Agent",
                          "input": {"description": description, "subagent_type": subagent_type,
                                    "prompt": "do the work"}}])
        return self

    def text(self, text: str):
        self._assistant([{"type": "text", "text": text}])
        return self

    def user_text(self, text: str):
        self._user(text)
        return self

    def subagent(self, agent_id: str, agent_type: str, description: str, tool_use_id: str | None = None):
        sub_dir = self.path.parent / self.sid / "subagents" if self.agent_id is None else self.path.parent
        meta = {"agentType": agent_type, "description": description}
        if tool_use_id is not None:
            meta["toolUseId"] = tool_use_id
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / f"agent-{agent_id}.meta.json").write_text(json.dumps(meta))
        writer = SessionWriter(self.tree, sub_dir / f"agent-{agent_id}.jsonl", self.sid, self.cwd,
                               self.branch, agent_id=agent_id)
        writer._user("You are a subagent.")
        return writer


def _usage(input: int, output: int, cache_read: int, cw5m: int = 0, cw1h: int = 0, kind: str | None = None) -> dict:
    usage = {
        "input_tokens": input,
        "output_tokens": output,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cw5m + cw1h,
        "cache_creation": {"ephemeral_5m_input_tokens": cw5m, "ephemeral_1h_input_tokens": cw1h},
    }
    if kind:
        usage["type"] = kind
    return usage
