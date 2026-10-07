# ABOUTME: End-to-end tests: run `beat` and `flush` as subprocesses, the way hooks and launchd do.
# ABOUTME: Includes the issue #97 success condition and the hook's silence guarantee.

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from conftest import OTHER, WAVELY

T0 = datetime(2026, 10, 6, 14, 0, tzinfo=UTC).timestamp()
MIN = 60


def run(args: list[str], state_dir: Path, config_file: Path, now: float, stdin: str = ""):
    env = {
        **os.environ,
        "TOGGL_HEARTBEAT_STATE_DIR": str(state_dir),
        "TOGGL_HEARTBEAT_CONFIG": str(config_file),
        "TOGGL_HEARTBEAT_NOW": str(now),
    }
    return subprocess.run(
        [sys.executable, "-m", "toggl_heartbeat", *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def hook_json(cwd: Path, session: str = "s1") -> str:
    return json.dumps(
        {
            "session_id": session,
            "cwd": str(cwd),
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
        }
    )


def test_beat_is_silent_and_appends_one_line(state_dir, config_file, home):
    result = run(["beat"], state_dir, config_file, T0, hook_json(home / "git-wavely" / "api"))
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
    lines = (state_dir / "heartbeats.jsonl").read_text().splitlines()
    assert [json.loads(line) for line in lines] == [
        {"ts": T0, "session": "s1", "cwd": str(home / "git-wavely" / "api")}
    ]


def test_beat_with_garbage_stdin_still_records_and_stays_silent(state_dir, config_file):
    for stdin in ["", "not json", "[1, 2]"]:
        result = run(["beat"], state_dir, config_file, T0, stdin)
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
    assert len((state_dir / "heartbeats.jsonl").read_text().splitlines()) == 3


def test_beat_stays_silent_when_state_dir_is_unwritable(tmp_path, config_file, home):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file where the state dir should be")
    result = run(["beat"], blocker / "state", config_file, T0, hook_json(home))
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_success_condition_three_entries_then_nothing(state_dir, config_file, home, toggl):
    api = home / "git-wavely" / "api"
    web = home / "git" / "acme" / "web"
    bursts = [(T0, api), (T0 + 25 * MIN, api), (T0 + 60 * MIN, web)]
    for start, cwd in bursts:
        for i in range(6):
            run(["beat"], state_dir, config_file, start + i * MIN, hook_json(cwd))

    first = run(["flush"], state_dir, config_file, T0 + 120 * MIN)
    assert (first.returncode, first.stderr) == (0, "")
    assert [(p["project_id"], p["start"]) for p in toggl.posts] == [
        (WAVELY, "2026-10-06T14:00:00Z"),
        (WAVELY, "2026-10-06T14:25:00Z"),
        (OTHER, "2026-10-06T15:00:00Z"),
    ]
    assert all(5 * MIN <= p["duration"] <= 6 * MIN for p in toggl.posts)

    second = run(["flush"], state_dir, config_file, T0 + 150 * MIN)
    assert (second.returncode, second.stderr) == (0, "")
    assert len(toggl.posts) == 3


def test_flush_reports_http_status_and_exits_nonzero(state_dir, config_file, home, toggl):
    run(["beat"], state_dir, config_file, T0, hook_json(home / "git-wavely" / "api"))
    toggl.fail_with = 500
    result = run(["flush"], state_dir, config_file, T0 + 30 * MIN)
    assert result.returncode == 1
    assert "500" in result.stderr
    assert (state_dir / "heartbeats.jsonl").read_text().strip() != ""
