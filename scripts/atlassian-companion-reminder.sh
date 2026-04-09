#!/usr/bin/env bash
# ABOUTME: PreToolUse hook body for mcp-atlassian.* tools.
# ABOUTME: Reminds the session to load the atlassian-companion skill first.
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Reminder: Load the atlassian-companion skill via the Skill tool before calling mcp-atlassian tools. It documents JQL quirks and parameter patterns that prevent silent failures."}}'
