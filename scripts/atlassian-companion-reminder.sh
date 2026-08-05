#!/usr/bin/env bash
# ABOUTME: PreToolUse hook body for Bash calls that invoke the acli Atlassian CLI.
# ABOUTME: Reminds the session to load the atlassian-companion skill first.
#
# Registered against the Bash matcher, so it fires on every Bash call and must
# decide for itself whether the command is an acli invocation. Silence (exit 0
# with no output) is the normal case.

set -euo pipefail

payload=$(cat)
command=$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')

# Require acli in command position AND followed by one of its actual
# subcommands. The subcommand check is what keeps prose out: a heredoc or an
# echo containing a sentence that starts "acli 1.3.22 replaces..." sits at the
# start of a line and is otherwise indistinguishable from an invocation.
if ! printf '%s' "$command" | grep -qE '(^|[;&|(])[[:space:]]*acli[[:space:]]+(jira|confluence|auth|admin|config|guard|rovodev)([[:space:]]|$)'; then
  exit 0
fi

printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Reminder: Load the atlassian-companion skill via the Skill tool before running acli commands. It documents the flag patterns, ADF description handling, and bulk-write guardrails that prevent malformed calls and accidental mass edits."}}'
