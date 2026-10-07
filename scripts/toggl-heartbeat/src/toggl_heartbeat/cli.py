# ABOUTME: Command-line entry point: `beat` records a heartbeat, `flush` posts to Toggl.
# ABOUTME: `beat` runs inside Claude Code hooks, so it must stay silent and always exit 0.

import json
import os
import sys
import time

from toggl_heartbeat import store
from toggl_heartbeat.blocks import Heartbeat


def now() -> float:
    override = os.environ.get("TOGGL_HEARTBEAT_NOW")
    return float(override) if override else time.time()


def beat() -> int:
    try:
        try:
            data = json.loads(sys.stdin.read())
        except ValueError:
            data = None
        if not isinstance(data, dict):
            data = {}
        heartbeat = Heartbeat(
            ts=now(),
            session=str(data.get("session_id") or "unknown"),
            cwd=str(data.get("cwd") or os.getcwd()),
        )
        store.append(store.state_dir(), heartbeat)
    except Exception:  # noqa: BLE001, S110 - a hook must never fail or print
        pass
    return 0


def flush() -> int:
    from toggl_heartbeat.config import config_path, load
    from toggl_heartbeat.flush import TogglError
    from toggl_heartbeat.flush import flush as run_flush

    directory = store.state_dir()
    try:
        with store.try_exclusive(directory, "flush.lock") as acquired:
            if not acquired:
                return 0
            run_flush(load(config_path()), directory, now())
    except (TogglError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"toggl-heartbeat flush: {error}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "beat":
        return beat()
    if command == "flush":
        return flush()
    print("usage: toggl-heartbeat beat|flush", file=sys.stderr)
    return 2
