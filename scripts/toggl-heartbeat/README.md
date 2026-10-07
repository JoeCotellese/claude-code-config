<!-- ABOUTME: Setup and behavior notes for toggl-heartbeat. -->
<!-- ABOUTME: Covers hooks, launchd flusher, config, and allocation rules. -->

# toggl-heartbeat

Bills Claude Code working time to Toggl per client, without depending on session start/end.

1. Hooks (`UserPromptSubmit`, `PostToolUse`, `Stop`) run `beat`, which appends a heartbeat
   (time, session, cwd) to `~/.local/state/toggl-heartbeat/heartbeats.jsonl`. No network, no output.
2. launchd runs `flush` every 15 minutes. It maps each cwd to a Toggl project, merges heartbeats
   into blocks, and posts finished entries for blocks whose idle window has passed.

## Allocation

1. A gap longer than `idle_minutes` ends a block. A block runs from its first heartbeat to its last
   plus `grace_minutes`.
2. Heartbeats for one project share a timeline across sessions, so parallel sub-repos of one client
   bill the union of time, not the sum.
3. Different clients active at once each get the full time.
4. The entry description and tags list the sub-repos (first directory under the rule prefix) in the block.

## Install

1. `uv sync` in this directory, then `make install` at the repo root to link it into `~/.claude/scripts`.
2. `cp config.example.toml ~/.config/toggl-heartbeat/config.toml` and edit the rules.
   Store the Toggl API token in the Keychain (repeat after rotating it):
   `security add-generic-password -U -s toggl-heartbeat -a api_token -w "$(op read 'op://Services/Toggl API Key/credential')"`
   Do not point `token_command` at `op read`: under launchd it fails with "authorization timeout".
3. Add hooks to `~/.claude/settings.json` for `UserPromptSubmit`, `PostToolUse`, and `Stop`:
   `~/.claude/scripts/toggl-heartbeat/.venv/bin/python -m toggl_heartbeat beat`
4. `sed "s|__HOME__|$HOME|g" launchd/com.cotellese.toggl-heartbeat.plist > ~/Library/LaunchAgents/com.cotellese.toggl-heartbeat.plist`
   then `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.cotellese.toggl-heartbeat.plist`.

Flush errors go to `~/.local/state/toggl-heartbeat/flush.log`. Heartbeats stay queued until a flush
succeeds.

## Known limits

1. A crash between a successful POST and the log rewrite posts that block again on the next flush.
2. The token is read only when a block is ready. If the read fails, that flush fails and retries.

## Tests

`uv run pytest`. The CLI tests are end to end: they run `beat` and `flush` as subprocesses against a
fake Toggl server.
