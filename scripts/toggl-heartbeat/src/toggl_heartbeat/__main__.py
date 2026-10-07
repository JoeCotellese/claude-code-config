# ABOUTME: Lets the package run as `python -m toggl_heartbeat`.
# ABOUTME: Delegates to the CLI entry point.

from toggl_heartbeat.cli import main

raise SystemExit(main())
