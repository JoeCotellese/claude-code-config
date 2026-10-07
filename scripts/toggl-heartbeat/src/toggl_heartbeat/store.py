# ABOUTME: The on-disk heartbeat log: one JSON object per line, guarded by a lock file.
# ABOUTME: Hooks append under the lock; flush snapshots, then removes only what it posted.

import fcntl
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from toggl_heartbeat.blocks import Heartbeat

DEFAULT_STATE_DIR = Path("~/.local/state/toggl-heartbeat")
LOG_NAME = "heartbeats.jsonl"


def state_dir() -> Path:
    override = os.environ.get("TOGGL_HEARTBEAT_STATE_DIR")
    return Path(override) if override else DEFAULT_STATE_DIR.expanduser()


@contextmanager
def _locked(directory: Path, name: str = "heartbeats.lock") -> Iterator[None]:
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / name, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


@contextmanager
def try_exclusive(directory: Path, name: str) -> Iterator[bool]:
    """Non-blocking lock; yields False when another process already holds it."""
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / name, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def append(directory: Path, beat: Heartbeat) -> None:
    with _locked(directory), open(directory / LOG_NAME, "a") as log:
        log.write(json.dumps(asdict(beat)) + "\n")


def _parse(line: str) -> Heartbeat | None:
    try:
        data = json.loads(line)
        return Heartbeat(ts=float(data["ts"]), session=str(data["session"]), cwd=str(data["cwd"]))
    except (ValueError, KeyError, TypeError):
        return None


def _lines(directory: Path) -> list[str]:
    path = directory / LOG_NAME
    return path.read_text().splitlines() if path.exists() else []


def snapshot(directory: Path) -> tuple[list[Heartbeat], list[int]]:
    """Return (heartbeats, line index of each heartbeat)."""
    with _locked(directory):
        lines = _lines(directory)
    beats: list[Heartbeat] = []
    line_ids: list[int] = []
    for index, line in enumerate(lines):
        beat = _parse(line)
        if beat is not None:
            beats.append(beat)
            line_ids.append(index)
    return beats, line_ids


def read(directory: Path) -> list[Heartbeat]:
    return snapshot(directory)[0]


def remove(directory: Path, consumed: set[int]) -> None:
    """Drop consumed and unparseable lines.

    The log is re-read under the lock, so lines appended since the snapshot are kept.
    """
    with _locked(directory):
        lines = _lines(directory)
        kept = [
            line
            for index, line in enumerate(lines)
            if index not in consumed and _parse(line) is not None
        ]
        tmp = directory / (LOG_NAME + ".tmp")
        tmp.write_text("".join(line + "\n" for line in kept))
        os.replace(tmp, directory / LOG_NAME)
