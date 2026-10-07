# ABOUTME: Unit tests for turning heartbeats into per-project billable blocks.
# ABOUTME: Covers gap merging, grace, same-client union, cross-client overlap, and completeness.

from toggl_heartbeat.blocks import Heartbeat, build_blocks, completed
from toggl_heartbeat.config import Config, Rule, resolve

HOME = "/Users/me"
WAVELY = 111
OTHER = 222
FALLBACK = 999
MIN = 60


def make_config(rules: list[Rule] | None = None) -> Config:
    return Config(
        workspace_id=1,
        token_command=["true"],
        idle_minutes=10,
        grace_minutes=1,
        billable=True,
        fallback_project_id=FALLBACK,
        api_base="http://unused",
        rules=rules
        or [
            Rule(prefix=f"{HOME}/git-wavely", project_id=WAVELY),
            Rule(prefix=f"{HOME}/git/acme", project_id=OTHER),
        ],
    )


def burst(start: int, minutes: int, cwd: str, session: str = "s1") -> list[Heartbeat]:
    return [Heartbeat(ts=start + i * MIN, session=session, cwd=cwd) for i in range(minutes + 1)]


def test_resolve_picks_longest_matching_prefix():
    config = make_config(
        rules=[
            Rule(prefix=f"{HOME}/git", project_id=OTHER),
            Rule(prefix=f"{HOME}/git/wavely", project_id=WAVELY),
        ]
    )
    assert resolve(config, f"{HOME}/git/wavely/backend") == (WAVELY, "backend")
    assert resolve(config, f"{HOME}/git/acme") == (OTHER, "acme")


def test_resolve_matches_on_path_boundaries_only():
    config = make_config()
    assert resolve(config, f"{HOME}/git-wavely-old/x") == (FALLBACK, "x")


def test_resolve_names_the_rule_root_itself_by_basename():
    config = make_config()
    assert resolve(config, f"{HOME}/git-wavely") == (WAVELY, "git-wavely")


def test_resolve_expands_tilde_in_rule_prefix():
    config = make_config(rules=[Rule(prefix="~/git-wavely", project_id=WAVELY)])
    import os

    assert resolve(config, os.path.expanduser("~/git-wavely/api")) == (WAVELY, "api")


def test_unmatched_cwd_goes_to_fallback():
    config = make_config()
    assert resolve(config, "/tmp/scratch") == (FALLBACK, "scratch")


def test_single_burst_is_one_block_with_grace():
    config = make_config()
    blocks = build_blocks(config, burst(0, 5, f"{HOME}/git-wavely/api"))
    assert len(blocks) == 1
    assert blocks[0].project_id == WAVELY
    assert blocks[0].start == 0
    assert blocks[0].duration == 6 * MIN


def test_gap_longer_than_idle_splits_blocks():
    config = make_config()
    beats = burst(0, 5, f"{HOME}/git-wavely/api") + burst(25 * MIN, 5, f"{HOME}/git-wavely/api")
    blocks = build_blocks(config, beats)
    assert [(b.start, b.duration) for b in blocks] == [(0, 6 * MIN), (25 * MIN, 6 * MIN)]


def test_gap_within_idle_joins_blocks():
    config = make_config()
    beats = burst(0, 5, f"{HOME}/git-wavely/api") + burst(14 * MIN, 5, f"{HOME}/git-wavely/api")
    blocks = build_blocks(config, beats)
    assert [(b.start, b.duration) for b in blocks] == [(0, 20 * MIN)]


def test_parallel_sub_repos_of_one_client_bill_the_union():
    config = make_config()
    beats = burst(0, 30, f"{HOME}/git-wavely/wavely-backend", "a") + burst(
        0, 30, f"{HOME}/git-wavely/react-native-wavelydx-v2", "b"
    )
    blocks = build_blocks(config, beats)
    assert len(blocks) == 1
    assert blocks[0].duration == 31 * MIN
    assert blocks[0].description == "react-native-wavelydx-v2, wavely-backend"


def test_cross_client_overlap_bills_each_client_in_full():
    config = make_config()
    beats = burst(0, 30, f"{HOME}/git-wavely/api", "a") + burst(0, 30, f"{HOME}/git/acme/web", "b")
    blocks = build_blocks(config, beats)
    assert sorted((b.project_id, b.duration) for b in blocks) == [
        (WAVELY, 31 * MIN),
        (OTHER, 31 * MIN),
    ]


def test_heartbeat_order_does_not_matter():
    config = make_config()
    beats = burst(0, 5, f"{HOME}/git-wavely/api")
    assert build_blocks(config, list(reversed(beats))) == build_blocks(config, beats)


def test_block_is_complete_only_after_idle_window_passes():
    config = make_config()
    [block] = build_blocks(config, burst(0, 5, f"{HOME}/git-wavely/api"))
    last_beat = 5 * MIN
    assert completed(config, [block], now=last_beat + 10 * MIN) == []
    assert completed(config, [block], now=last_beat + 10 * MIN + 1) == [block]


def test_block_remembers_which_heartbeats_it_consumed():
    config = make_config()
    beats = burst(0, 2, f"{HOME}/git-wavely/api") + burst(0, 2, f"{HOME}/git/acme/web")
    blocks = build_blocks(config, beats)
    consumed = sorted(i for b in blocks for i in b.heartbeat_ids)
    assert consumed == list(range(len(beats)))
