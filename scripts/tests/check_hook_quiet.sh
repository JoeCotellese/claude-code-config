#!/bin/bash
# ABOUTME: Test for dev-jawn's hook quiet-mode marker (CLAUDE.md `dev-jawn: quiet`).
# ABOUTME: Asserts the workflow hook injects normally, and stays silent when a repo opts out.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK="$REPO_ROOT/plugins/dev-jawn/hooks/workflow-policy.sh"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Without a marker, the hook injects the workflow policy.
out="$(CLAUDE_PROJECT_DIR="$TMP" bash "$HOOK" 2>/dev/null)"
if printf '%s' "$out" | grep -q 'Git Workflow (CRITICAL)'; then
    pass "no marker: hook injects the workflow policy"
else
    bad "no marker: hook did not inject the policy"
fi

# Marker in CLAUDE.md silences the hook.
printf '# Project\n<!-- dev-jawn: quiet -->\n' > "$TMP/CLAUDE.md"
out="$(CLAUDE_PROJECT_DIR="$TMP" bash "$HOOK" 2>/dev/null)"
if [ -z "$out" ]; then
    pass "CLAUDE.md marker: hook injects nothing"
else
    bad "CLAUDE.md marker: hook still emitted output"
fi
rm -f "$TMP/CLAUDE.md"

# Marker in .claude/CLAUDE.md also silences it.
mkdir -p "$TMP/.claude"
printf 'dev-jawn: quiet\n' > "$TMP/.claude/CLAUDE.md"
out="$(CLAUDE_PROJECT_DIR="$TMP" bash "$HOOK" 2>/dev/null)"
if [ -z "$out" ]; then
    pass ".claude/CLAUDE.md marker: hook injects nothing"
else
    bad ".claude/CLAUDE.md marker: hook still emitted output"
fi

echo
if [ "$fail" -eq 0 ]; then
    echo "RESULT: PASS — hook quiet-mode marker works."
else
    echo "RESULT: FAIL — hook quiet-mode marker broken."
fi
exit "$fail"
