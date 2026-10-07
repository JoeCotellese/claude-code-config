# ABOUTME: Loads the TOML config and maps a working directory to a Toggl project.
# ABOUTME: Rules match on path prefix; the longest matching prefix wins, else the fallback.

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("~/.config/toggl-heartbeat/config.toml")
DEFAULT_API_BASE = "https://api.track.toggl.com/api/v9"


@dataclass(frozen=True)
class Rule:
    prefix: str
    project_id: int


@dataclass(frozen=True)
class Config:
    workspace_id: int
    token_command: list[str]
    fallback_project_id: int
    idle_minutes: int = 10
    grace_minutes: int = 1
    billable: bool = True
    api_base: str = DEFAULT_API_BASE
    rules: list[Rule] = field(default_factory=list)


def config_path() -> Path:
    override = os.environ.get("TOGGL_HEARTBEAT_CONFIG")
    return Path(override) if override else DEFAULT_CONFIG_PATH.expanduser()


def load(path: Path) -> Config:
    data = tomllib.loads(path.read_text())
    rules = [
        Rule(prefix=r["prefix"], project_id=int(r["project_id"])) for r in data.pop("rule", [])
    ]
    config = Config(**data, rules=rules)
    if config.grace_minutes > config.idle_minutes:
        raise ValueError("grace_minutes must not exceed idle_minutes")
    return config


def resolve(config: Config, cwd: str) -> tuple[int, str]:
    """Return (project_id, label) for a cwd. The label is the sub-repo under the rule root."""
    path = Path(cwd)
    best: tuple[Path, int] | None = None
    for rule in config.rules:
        root = Path(os.path.expanduser(rule.prefix))
        if (path == root or root in path.parents) and (
            best is None or len(root.parts) > len(best[0].parts)
        ):
            best = (root, rule.project_id)
    if best is None:
        return config.fallback_project_id, path.name
    root, project_id = best
    if path == root:
        return project_id, root.name
    return project_id, path.relative_to(root).parts[0]
