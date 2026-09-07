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

# --- Code review consolidation: one review, in /submit ---
# Reverting any part of the consolidation flips one of these to FAIL.

IMPL="$SKILLS/implement/SKILL.md"
SUBMIT="$SKILLS/submit/SKILL.md"
AGENTS="$PLUGIN/agents"

# /implement no longer reviews its own work.
if grep -q '^### Step .*: Code Review' "$IMPL"; then
    bad "CR /implement still has a Code Review step"
else
    pass "CR /implement has no Code Review step"
fi
for r in swift-swiftui-reviewer python-code-reviewer cpp-qt-reviewer; do
    if grep -q "$r" "$IMPL"; then
        bad "CR /implement still routes to $r"
    else
        pass "CR /implement does not route to $r"
    fi
done

# The TDD compliance check moved rather than being deleted.
if grep -q 'Tests should appear in commits' "$SUBMIT"; then
    pass "CR TDD compliance check lives in /submit"
else
    bad "CR TDD compliance check lost in the move"
fi

# /submit delegates the generic sweep to the built-in code-review skill.
if grep -q 'skill="code-review"' "$SUBMIT"; then
    pass "CR /submit invokes the built-in code-review skill"
else
    bad "CR /submit does not invoke the built-in code-review skill"
fi
for tier in 'effort/S.*code-review low' 'effort/M.*code-review medium' 'effort/L.*code-review high'; do
    if grep -Eq "$tier" "$SUBMIT"; then
        pass "CR /submit maps $(echo "$tier" | cut -d. -f1)"
    else
        bad "CR /submit missing tier mapping: $tier"
    fi
done

# Lens A and Lens C are real agents with their own effort, namespaced for the plugin.
for a in acceptance-criteria-reviewer test-adequacy-reviewer; do
    if [ -f "$AGENTS/$a.md" ]; then pass "CR agent present: $a"; else bad "CR agent missing: $a"; fi
    if grep -q "^effort: high" "$AGENTS/$a.md" 2>/dev/null; then
        pass "CR agent $a carries its own effort"
    else
        bad "CR agent $a does not set effort: high"
    fi
    if grep -q "subagent_type=\"dev-jawn:$a\"" "$SUBMIT"; then
        pass "CR /submit calls $a by its namespaced type"
    else
        bad "CR /submit does not call dev-jawn:$a"
    fi
done

# /submit orchestrates; depth lives in the reviewers.
if grep -q '^effort: low' "$SUBMIT"; then
    pass "CR /submit runs at effort: low"
else
    bad "CR /submit is not at effort: low"
fi

# --- Issue #53: domain gate is enrichment, not a blocker ---
# Reverting the SKILL.md or detector change flips one of these to FAIL.

DETECT="$SKILLS/submit/scripts/detect_project_domain.sh"

# AC1 — an unknown domain continues the committee instead of stopping it.
if grep -Eiq 'unknown.*STOP' "$SUBMIT"; then
    bad "DOMAIN unknown still routes to STOP in /submit"
else
    pass "DOMAIN unknown does not stop submit"
fi
if grep -Eiq 'unknown.*(continue|acknowledg)' "$SUBMIT"; then
    pass "DOMAIN unknown routes to acknowledge-and-continue"
else
    bad "DOMAIN unknown has no acknowledge-and-continue route"
fi

# AC2 — the error handling table carries the collision case, not an unknown stop.
if grep -Eiq '^\|.*unknown.*STOP' "$SUBMIT"; then
    bad "DOMAIN error table still stops on unknown"
else
    pass "DOMAIN error table has no unknown stop"
fi
if grep -Eiq '^\|.*ambiguous.*STOP' "$SUBMIT"; then
    pass "DOMAIN error table stops on ambiguous"
else
    bad "DOMAIN error table missing ambiguous stop row"
fi

# AC3 — the three real reviewer routes survive the change.
for r in swift-swiftui-reviewer python-code-reviewer cpp-qt-reviewer; do
    if grep -q "$r" "$SUBMIT"; then
        pass "DOMAIN reviewer route intact: $r"
    else
        bad "DOMAIN reviewer route lost: $r"
    fi
done

# AC4 — the detector reports a collision instead of resolving by precedence.
if [ -f "$DETECT" ]; then
    D_TMP="$(mktemp -d)"
    : > "$D_TMP/Package.swift"
    : > "$D_TMP/pyproject.toml"
    d_out="$(bash "$DETECT" "$D_TMP" 2>/dev/null)"
    rm -rf "$D_TMP"
    if printf '%s' "$d_out" | grep -q '^ambiguous:' \
       && printf '%s' "$d_out" | grep -q 'swift' \
       && printf '%s' "$d_out" | grep -q 'python'; then
        pass "DOMAIN detector reports collision (got: $d_out)"
    else
        bad "DOMAIN detector did not report collision (got: $d_out)"
    fi

    # Single-domain and no-domain detection must still work.
    for pair in "Package.swift:swift" "pyproject.toml:python" "app.pro:cpp-qt"; do
        marker="${pair%%:*}"; want="${pair##*:}"
        D_TMP="$(mktemp -d)"
        : > "$D_TMP/$marker"
        got="$(bash "$DETECT" "$D_TMP" 2>/dev/null)"
        rm -rf "$D_TMP"
        if [ "$got" = "$want" ]; then
            pass "DOMAIN detector single-domain $want"
        else
            bad "DOMAIN detector $marker returned '$got', want '$want'"
        fi
    done
    D_TMP="$(mktemp -d)"
    got="$(bash "$DETECT" "$D_TMP" 2>/dev/null)"
    rm -rf "$D_TMP"
    if [ "$got" = "unknown" ]; then
        pass "DOMAIN detector empty repo is unknown"
    else
        bad "DOMAIN detector empty repo returned '$got', want 'unknown'"
    fi
else
    bad "DOMAIN detector script missing: $DETECT"
fi

# AC5 — ambiguous is the only domain condition that stops a submission.
if grep -Eiq 'ambiguous.*STOP|STOP.*ambiguous' "$SUBMIT"; then
    pass "DOMAIN stop is reserved for the ambiguous case"
else
    bad "DOMAIN ambiguous case does not stop /submit"
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
