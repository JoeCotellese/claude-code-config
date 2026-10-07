# ABOUTME: Shared fixtures: a fake Toggl API server and a config pointing at it.
# ABOUTME: The fake records every POST and can be told to fail with a given status.

import base64
import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TOKEN = "test-token"
WORKSPACE = 42
WAVELY = 111
OTHER = 222
FALLBACK = 999


@dataclass
class FakeToggl:
    url: str
    posts: list[dict] = field(default_factory=list)
    fail_with: int | None = None


@pytest.fixture
def toggl():
    fake = FakeToggl(url="")
    expected_auth = "Basic " + base64.b64encode(f"{TOKEN}:api_token".encode()).decode()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if self.headers.get("Authorization") != expected_auth:
                self._reply(403, {"error": "bad auth"})
            elif self.path != f"/api/v9/workspaces/{WORKSPACE}/time_entries":
                self._reply(404, {"error": self.path})
            elif fake.fail_with:
                self._reply(fake.fail_with, {"error": "induced"})
            else:
                fake.posts.append(body)
                self._reply(200, {"id": len(fake.posts), **body})

        def _reply(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    fake.url = f"http://127.0.0.1:{server.server_port}/api/v9"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield fake
    server.shutdown()
    server.server_close()


@pytest.fixture
def home(tmp_path: Path) -> Path:
    path = tmp_path / "home"
    (path / "git-wavely").mkdir(parents=True)
    return path


@pytest.fixture
def token_marker(tmp_path: Path) -> Path:
    return tmp_path / "token-was-read"


@pytest.fixture
def config_file(tmp_path: Path, home: Path, toggl: FakeToggl, token_marker: Path) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(
        f"""
workspace_id = {WORKSPACE}
token_command = ["sh", "-c", "touch '{token_marker}'; echo {TOKEN}"]
idle_minutes = 10
grace_minutes = 1
billable = true
fallback_project_id = {FALLBACK}
api_base = "{toggl.url}"

[[rule]]
prefix = "{home}/git-wavely"
project_id = {WAVELY}

[[rule]]
prefix = "{home}/git/acme"
project_id = {OTHER}
"""
    )
    return path


@pytest.fixture
def state_dir(tmp_path: Path) -> Path:
    return tmp_path / "state"
