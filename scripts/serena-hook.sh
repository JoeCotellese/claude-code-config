#!/usr/bin/env bash
# ABOUTME: Hook body wrapper for the serena-hooks CLI.
# ABOUTME: Invoked by Claude Code hooks in ~/.claude/settings.json.
exec serena-hooks "$1" --client=claude-code
