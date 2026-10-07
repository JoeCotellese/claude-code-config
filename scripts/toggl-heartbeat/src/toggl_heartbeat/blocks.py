# ABOUTME: Merges heartbeats into per-project blocks of busy time.
# ABOUTME: Same-project heartbeats from any session share one timeline, so overlap bills once.

from collections import defaultdict
from dataclasses import dataclass

from toggl_heartbeat.config import Config, resolve


@dataclass(frozen=True)
class Heartbeat:
    ts: float
    session: str
    cwd: str


@dataclass(frozen=True)
class Block:
    project_id: int
    start: float
    last_beat: float
    duration: float
    labels: tuple[str, ...]
    heartbeat_ids: tuple[int, ...]

    @property
    def description(self) -> str:
        return ", ".join(self.labels)


def build_blocks(config: Config, beats: list[Heartbeat]) -> list[Block]:
    """Group by project, then split each project's sorted heartbeats wherever the gap exceeds idle.

    heartbeat_ids are indexes into `beats`, so callers can drop exactly what was posted.
    """
    idle = config.idle_minutes * 60
    grace = config.grace_minutes * 60
    by_project: dict[int, list[tuple[float, str, int]]] = defaultdict(list)
    for index, beat in enumerate(beats):
        project_id, label = resolve(config, beat.cwd)
        by_project[project_id].append((beat.ts, label, index))

    blocks: list[Block] = []
    for project_id, entries in by_project.items():
        entries.sort()
        run = [entries[0]]
        for entry in entries[1:]:
            if entry[0] - run[-1][0] > idle:
                blocks.append(_close(project_id, run, grace))
                run = []
            run.append(entry)
        blocks.append(_close(project_id, run, grace))
    return sorted(blocks, key=lambda b: (b.start, b.project_id))


def _close(project_id: int, run: list[tuple[float, str, int]], grace: float) -> Block:
    start, last = run[0][0], run[-1][0]
    return Block(
        project_id=project_id,
        start=start,
        last_beat=last,
        duration=last - start + grace,
        labels=tuple(sorted({label for _, label, _ in run})),
        heartbeat_ids=tuple(sorted(index for _, _, index in run)),
    )


def completed(config: Config, blocks: list[Block], now: float) -> list[Block]:
    """Blocks no future heartbeat can extend: the idle window after the last beat has passed."""
    idle = config.idle_minutes * 60
    return [b for b in blocks if now - b.last_beat > idle]
