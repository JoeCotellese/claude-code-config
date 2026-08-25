#!/bin/bash
# ABOUTME: Acceptance test for issue #26 (dev-jawn workflow plugin).
# ABOUTME: Checks the file/grep invariants that map to the issue's acceptance criteria; fails until dev-jawn ships.

# Derived from #26 acceptance criteria at the Definition of Ready gate, before
# implementation. Runs the shell-checkable invariants. The runtime-toggle
# criteria (AC1/AC3/AC4) are [manual] in a live Claude Code session; this script
# provides their automatable proxies where one exists.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PLUGIN="plugins/dev-jawn"
SKILLS="$PLUGIN/skills"
HOOK="$PLUGIN/hooks/workflow-policy.sh"
PHASE_SKILLS="spec ready ui-design implement verify submit retro create-goal"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

# AC8 — plugin subtree exists with all eight skills, WORKFLOW.md, cpr, and the hook.
for s in $PHASE_SKILLS; do
    if [ -f "$SKILLS/$s/SKILL.md" ]; then pass "AC8 skill present: $s"; else bad "AC8 skill missing: $s"; fi
done
[ -f "$SKILLS/WORKFLOW.md" ]        && pass "AC8 WORKFLOW.md present"        || bad "AC8 WORKFLOW.md missing"
[ -f "$PLUGIN/commands/cpr.md" ]    && pass "AC8 cpr command present"        || bad "AC8 cpr command missing"
[ -x "$HOOK" ]                      && pass "AC8 workflow-policy.sh executable" || bad "AC8 workflow-policy.sh missing or not executable"

# AC2 — no absolute ~/.claude/skills path coupling remains inside the plugin.
if [ -d "$PLUGIN" ]; then
    if grep -rlq '~/.claude/skills' "$PLUGIN" 2>/dev/null; then
        bad "AC2 absolute ~/.claude/skills refs remain in $PLUGIN"
    else
        pass "AC2 no ~/.claude/skills refs in $PLUGIN"
    fi
else
    bad "AC2 $PLUGIN does not exist"
fi

# AC5 — CLAUDE.md carve-out: no workflow-specific policy remains.
if grep -q 'Git Workflow (CRITICAL)' CLAUDE.md 2>/dev/null; then
    bad "AC5 CLAUDE.md still contains 'Git Workflow (CRITICAL)' section"
else
    pass "AC5 CLAUDE.md has no 'Git Workflow (CRITICAL)' section"
fi
if grep -q 'invoke a phase skill IMMEDIATELY' CLAUDE.md 2>/dev/null; then
    bad "AC5 CLAUDE.md still contains phase-routing rule"
else
    pass "AC5 CLAUDE.md has no phase-routing rule"
fi

# AC3 (proxy) — the hook emits the workflow policy markers when run standalone.
# Run it against a marker-free temp dir so this checks the hook's DEFAULT injection behavior,
# independent of whether the repo it executes in has opted into quiet mode (dev-jawn: quiet in
# CLAUDE.md). Without this, marking this repo quiet would falsely fail AC3.
if [ -x "$HOOK" ]; then
    AC3_TMP="$(mktemp -d)"
    out="$(CLAUDE_PROJECT_DIR="$AC3_TMP" "$HOOK" 2>/dev/null)"
    rm -rf "$AC3_TMP"
    echo "$out" | grep -qi 'never commit' && echo "$out" | grep -qiE 'phase skill|/ready|/implement' \
        && pass "AC3 hook output carries never-commit + phase-routing policy" \
        || bad "AC3 hook output missing policy markers"
else
    bad "AC3 hook not runnable"
fi

# AC6 — stale atlassian MCP PreToolUse hook removed.
if grep -q 'mcp__mcp-atlassian__' .claude-plugin/plugin.json 2>/dev/null; then
    bad "AC6 stale mcp__mcp-atlassian__ matcher still in plugin.json"
else
    pass "AC6 no mcp__mcp-atlassian__ matcher in plugin.json"
fi

# AC7 — marketplace lists dev-jawn as an installable plugin.
if grep -q 'dev-jawn' .claude-plugin/marketplace.json 2>/dev/null; then
    pass "AC7 marketplace.json lists dev-jawn"
else
    bad "AC7 marketplace.json does not list dev-jawn"
fi

echo
if [ "$fail" -eq 0 ]; then
    echo "RESULT: PASS — dev-jawn shell invariants hold."
    echo "Remember the [manual] runtime checks: enable dev-jawn with zero ~/.claude/skills symlinks,"
    echo "confirm the 8 phase commands resolve (AC1), the policy is in context (AC3), then disable and"
    echo "confirm the policy AND commands are gone (AC4)."
else
    echo "RESULT: FAIL — dev-jawn not yet shipped (expected before implementation)."
fi
exit "$fail"
