# ABOUTME: Integration tests for flush: heartbeat log on disk, token command, and HTTP to a fake Toggl.
# ABOUTME: Checks what gets posted, what stays queued, and that nothing is posted twice.

from datetime import UTC, datetime
from pathlib import Path

import pytest
from conftest import FALLBACK, OTHER, WAVELY, WORKSPACE

from toggl_heartbeat import store
from toggl_heartbeat.blocks import Heartbeat
from toggl_heartbeat.config import load
from toggl_heartbeat.flush import TogglError, flush

T0 = datetime(2026, 10, 6, 14, 0, tzinfo=UTC).timestamp()
MIN = 60


def beat_burst(state_dir: Path, start: float, minutes: int, cwd: Path, session: str = "s1"):
    for i in range(minutes + 1):
        store.append(state_dir, Heartbeat(ts=start + i * MIN, session=session, cwd=str(cwd)))


def test_posts_completed_block_as_finished_billable_entry(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "wavely-backend")
    flush(load(config_file), state_dir, now=T0 + 30 * MIN)
    assert toggl.posts == [
        {
            "created_with": "toggl-heartbeat",
            "workspace_id": WORKSPACE,
            "project_id": WAVELY,
            "description": "wavely-backend",
            "start": "2026-10-06T14:00:00Z",
            "duration": 6 * MIN,
            "billable": True,
            "tags": ["wavely-backend"],
        }
    ]


def test_second_flush_posts_nothing(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    config = load(config_file)
    flush(config, state_dir, now=T0 + 30 * MIN)
    flush(config, state_dir, now=T0 + 60 * MIN)
    assert len(toggl.posts) == 1


def test_parallel_wavely_sub_repos_post_one_entry(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 30, home / "git-wavely" / "wavely-backend", "a")
    beat_burst(state_dir, T0, 30, home / "git-wavely" / "react-native-wavelydx-v2", "b")
    flush(load(config_file), state_dir, now=T0 + 60 * MIN)
    assert [(p["project_id"], p["duration"]) for p in toggl.posts] == [(WAVELY, 31 * MIN)]
    assert toggl.posts[0]["description"] == "react-native-wavelydx-v2, wavely-backend"
    assert toggl.posts[0]["tags"] == ["react-native-wavelydx-v2", "wavely-backend"]


def test_fallback_entry_is_tagged_with_its_repo(config_file, state_dir, toggl, tmp_path):
    beat_burst(state_dir, T0, 2, tmp_path / "git" / "mailjawn")
    flush(load(config_file), state_dir, now=T0 + 30 * MIN)
    assert [(p["project_id"], p["tags"]) for p in toggl.posts] == [(FALLBACK, ["mailjawn"])]


def test_cross_client_overlap_posts_full_time_to_each(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 30, home / "git-wavely" / "api", "a")
    beat_burst(state_dir, T0, 30, home / "git" / "acme" / "web", "b")
    flush(load(config_file), state_dir, now=T0 + 60 * MIN)
    assert sorted((p["project_id"], p["duration"]) for p in toggl.posts) == [
        (WAVELY, 31 * MIN),
        (OTHER, 31 * MIN),
    ]


def test_in_progress_block_waits_for_a_later_flush(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    config = load(config_file)
    flush(config, state_dir, now=T0 + 10 * MIN)
    assert toggl.posts == []
    beat_burst(state_dir, T0 + 12 * MIN, 3, home / "git-wavely" / "api")
    flush(config, state_dir, now=T0 + 40 * MIN)
    assert [(p["start"], p["duration"]) for p in toggl.posts] == [
        ("2026-10-06T14:00:00Z", 16 * MIN)
    ]


def test_unmatched_cwd_posts_to_fallback(config_file, state_dir, toggl, tmp_path):
    beat_burst(state_dir, T0, 2, tmp_path / "elsewhere")
    flush(load(config_file), state_dir, now=T0 + 30 * MIN)
    assert [p["project_id"] for p in toggl.posts] == [FALLBACK]


def test_toggl_error_keeps_heartbeats_for_next_flush(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    config = load(config_file)
    toggl.fail_with = 500
    with pytest.raises(TogglError, match="500"):
        flush(config, state_dir, now=T0 + 30 * MIN)
    assert toggl.posts == []
    toggl.fail_with = None
    flush(config, state_dir, now=T0 + 31 * MIN)
    assert len(toggl.posts) == 1


def test_partial_failure_keeps_only_unposted_blocks(config_file, state_dir, home, toggl):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    beat_burst(state_dir, T0 + 60 * MIN, 5, home / "git-wavely" / "api")
    config = load(config_file)
    flush(config, state_dir, now=T0 + 30 * MIN)
    toggl.fail_with = 503
    with pytest.raises(TogglError):
        flush(config, state_dir, now=T0 + 90 * MIN)
    toggl.fail_with = None
    flush(config, state_dir, now=T0 + 91 * MIN)
    assert [p["start"] for p in toggl.posts] == ["2026-10-06T14:00:00Z", "2026-10-06T15:00:00Z"]


def test_no_completed_blocks_means_no_token_read(config_file, state_dir, home, toggl, token_marker):
    flush(load(config_file), state_dir, now=T0)
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    flush(load(config_file), state_dir, now=T0 + 6 * MIN)
    assert not token_marker.exists()
    assert toggl.posts == []


def test_heartbeats_appended_during_flush_survive(config_file, state_dir, home, toggl, monkeypatch):
    beat_burst(state_dir, T0, 5, home / "git-wavely" / "api")
    late = Heartbeat(ts=T0 + 29 * MIN, session="s2", cwd=str(home / "git-wavely" / "api"))

    import toggl_heartbeat.flush as flush_module

    real_post = flush_module.post_entry

    def post_then_beat(*args, **kwargs):
        real_post(*args, **kwargs)
        store.append(state_dir, late)

    monkeypatch.setattr(flush_module, "post_entry", post_then_beat)
    flush(load(config_file), state_dir, now=T0 + 30 * MIN)
    assert store.read(state_dir) == [late]
