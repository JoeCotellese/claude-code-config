# ABOUTME: Posts completed heartbeat blocks to Toggl as finished time entries.
# ABOUTME: Reads the API token only when there is something to post.

import base64
import json
import subprocess
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from toggl_heartbeat import store
from toggl_heartbeat.blocks import Block, build_blocks, completed
from toggl_heartbeat.config import Config


class TogglError(Exception):
    pass


def read_token(config: Config) -> str:
    result = subprocess.run(config.token_command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise TogglError(f"token command exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def post_entry(config: Config, token: str, block: Block) -> None:
    body = {
        "created_with": "toggl-heartbeat",
        "workspace_id": config.workspace_id,
        "project_id": block.project_id,
        "description": block.description,
        "start": datetime.fromtimestamp(block.start, UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": round(block.duration),
        "billable": config.billable,
        "tags": list(block.labels),
    }
    auth = base64.b64encode(f"{token}:api_token".encode()).decode()
    request = urllib.request.Request(
        f"{config.api_base}/workspaces/{config.workspace_id}/time_entries",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30):
            pass
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:200]
        raise TogglError(f"Toggl returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise TogglError(f"could not reach Toggl: {error.reason}") from error


def flush(config: Config, state_dir: Path, now: float) -> int:
    """Post every completed block; return how many were posted.

    Each block's heartbeats are removed only after its POST succeeds, so a failure
    leaves the rest queued for the next run.
    """
    beats, line_ids = store.snapshot(state_dir)
    ready = completed(config, build_blocks(config, beats), now)
    if not ready:
        return 0
    token = read_token(config)
    posted: set[int] = set()
    try:
        for block in ready:
            post_entry(config, token, block)
            posted.update(line_ids[i] for i in block.heartbeat_ids)
    finally:
        if posted:
            store.remove(state_dir, posted)
    return len(ready)
