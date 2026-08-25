#!/bin/bash
# ABOUTME: Acceptance test for issue #37 (dev-jawn routing-label axis).
# ABOUTME: Checks the file/grep + label invariants that map to the issue's acceptance criteria; fails until shipped.

# Derived from #37 acceptance criteria at the Definition of Ready gate, before
# implementation. Every AC is [test: scripts/tests/check_issue_37.sh]: a shell
# invariant over the skill markdown and the repo's GitHub labels. Label checks
# (AC1/AC2) query `gh label list`, the same channel /spec uses to create them,
# and fail closed when gh is unavailable rather than reporting a false pass.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

SPEC="plugins/dev-jawn/skills/spec/SKILL.md"
READY="plugins/dev-jawn/skills/ready/SKILL.md"
UIDESIGN="plugins/dev-jawn/skills/ui-design/SKILL.md"
WORKFLOW="plugins/dev-jawn/skills/WORKFLOW.md"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

# Snapshot the repo's labels once. Fail closed if gh cannot answer.
LABELS=""
if command -v gh >/dev/null 2>&1; then
    LABELS="$(gh label list --limit 200 2>/dev/null | cut -f1)"
    GH_OK=1
else
    GH_OK=0
fi
has_label() { [ "$GH_OK" -eq 1 ] && printf '%s\n' "$LABELS" | grep -qxF "$1"; }

# AC1 — the six routing labels exist in the repo.
for L in gate:machine gate:human gate:mixed unattended blocked needs-design; do
    if has_label "$L"; then pass "AC1 routing label present: $L"
    elif [ "$GH_OK" -eq 0 ]; then bad "AC1 cannot verify label '$L' (gh unavailable)"
    else bad "AC1 routing label missing: $L"; fi
done

# AC2 — the missing priority labels exist, reconciling docs with the repo.
for L in value/L effort/L effort/XL; do
    if has_label "$L"; then pass "AC2 priority label present: $L"
    elif [ "$GH_OK" -eq 0 ]; then bad "AC2 cannot verify label '$L' (gh unavailable)"
    else bad "AC2 priority label missing: $L"; fi
done

# AC3 — /spec Step 6 documents gate classification, and the create command applies a gate: label.
if grep -qiE 'gate.?classif|classif.*gate|who closes it' "$SPEC" \
   && grep -qE -- '--label +"?gate:' "$SPEC"; then
    pass "AC3 spec documents gate classification and applies a gate: label"
else
    bad "AC3 spec missing gate classification step or gate: label in create command"
fi

# AC4 — the value table drops value/XL; the effort table keeps effort/XL.
if grep -q 'Critical capability, blocks major goals' "$SPEC"; then
    bad "AC4 value table still lists value/XL"
elif ! grep -q 'Epic-level' "$SPEC"; then
    bad "AC4 effort/XL row (Epic-level) missing from spec"
else
    pass "AC4 value/XL dropped, effort/XL retained"
fi

# AC5 — R8 (gate is set) is a Definition of Ready criterion in both ready and WORKFLOW.
if grep -qE '\bR8\b' "$READY" && grep -qiE 'R8.*gate|gate.*set' "$READY" \
   && grep -qE '\bR8\b' "$WORKFLOW"; then
    pass "AC5 R8 gate-is-set criterion present in ready and WORKFLOW"
else
    bad "AC5 R8 gate-is-set criterion missing from ready and/or WORKFLOW"
fi

# AC6 — /ui-design clears the needs-design label on its final approved pass.
if grep -qiE 'needs-design' "$UIDESIGN" \
   && grep -qiE '(remove|clear|delete).{0,40}needs-design|needs-design.{0,40}(remove|clear|delete)' "$UIDESIGN"; then
    pass "AC6 ui-design clears needs-design on final pass"
else
    bad "AC6 ui-design does not state it clears needs-design"
fi

# AC7 — WORKFLOW documents the routing axis + pull query, and marks polish a work-type tag.
if grep -qiE 'routing' "$WORKFLOW" \
   && grep -qE 'gate:machine' "$WORKFLOW" \
   && grep -qiE 'polish' "$WORKFLOW"; then
    pass "AC7 WORKFLOW documents routing axis, pull query, and polish note"
else
    bad "AC7 WORKFLOW missing routing axis / pull query / polish note"
fi

echo
if [ "$fail" -eq 0 ]; then
    echo "RESULT: PASS — issue #37 routing-label invariants hold."
else
    echo "RESULT: FAIL — routing-label axis not yet shipped (expected before implementation)."
fi
exit "$fail"
