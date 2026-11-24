#!/bin/bash
# ABOUTME: Acceptance test for issue #134 (/cost report and snapshot: token pressure per issue).
# ABOUTME: Runs the named unit tests for each [test:] criterion plus the skill-wiring invariants; fails until shipped.

# Derived from #134's acceptance criteria at the Definition of Ready gate, before
# implementation. The /cost script is program logic, not markdown, so R7 is not
# exempt: each [test:] criterion maps to exactly one named unittest method below,
# run by name (never the whole suite). AC13 and AC15 also need the skills to call
# the script, checked by the grep invariants at the end. AC17 is [manual]: it
# checks real #1118 transcripts on this machine; its proxies are AC1 and AC7.
#
# The interface (CLI flags, fixture layout, where bindings come from) is
# /architecture's call. This file fixes only the test module path and the
# method names, one per criterion.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PLUGIN="plugins/dev-jawn"
TEST_DIR="$PLUGIN/scripts/cost/tests"
MODULE="test_cost"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

TESTS="
AC1:test_ac01_bound_session_counts_main_and_subagents_per_phase
AC2:test_ac02_first_binding_backdates_to_session_start
AC3:test_ac03_nested_subagents_roll_up_to_spawning_phase
AC4:test_ac04_two_issue_spawn_splits_evenly_and_is_marked_shared
AC5:test_ac05_unbound_tokens_land_on_unattributed_and_lines_sum
AC6:test_ac06_repeated_phase_reports_attempts_and_rework
AC7:test_ac07_weighting_peak_context_and_share_over_200k
AC8:test_ac08_unknown_model_warns_and_uses_opus_weight
AC9:test_ac09_malformed_usage_record_exits_nonzero_with_file_and_line
AC10:test_ac10_session_view_lists_each_issue_and_unattributed
AC11:test_ac11_top_pressure_names_agent_with_most_tokens_over_200k
AC12:test_ac12_outcome_and_dod_round_count
AC13:test_ac13_snapshot_written_with_phases_models_version_and_time
AC14:test_ac14_snapshot_used_when_transcripts_absent
AC16:test_ac16_nothing_found_reports_and_exits_zero
"

if [ ! -f "$TEST_DIR/$MODULE.py" ]; then
    bad "test module missing at $TEST_DIR/$MODULE.py"
else
    for entry in $TESTS; do
        ac=${entry%%:*}
        name=${entry#*:}
        if out=$(cd "$TEST_DIR" && python3 -m unittest "$MODULE.CostTests.$name" 2>&1); then
            pass "$ac $name"
        else
            bad "$ac $name"
            printf '%s\n' "$out" | tail -5 | sed 's/^/      /'
        fi
    done
fi

# --- Skill wiring ----------------------------------------------------------
COST_SKILL="$PLUGIN/skills/cost/SKILL.md"
if [ -f "$COST_SKILL" ] && grep -q '^name: cost$' "$COST_SKILL"; then
    pass "cost skill exists as /cost (any session, any repo)"
else
    bad "cost skill missing at $COST_SKILL with 'name: cost'"
fi

# AC13: /submit writes and commits the snapshot before marking the PR ready.
if grep -q '\.dev-jawn/cost/' "$PLUGIN/skills/submit/SKILL.md"; then
    pass "AC13 submit/SKILL.md commits the .dev-jawn/cost/ snapshot"
else
    bad "AC13 submit/SKILL.md does not mention the .dev-jawn/cost/ snapshot"
fi

# AC15: autopilot's final report carries the one-line cost summary.
if sed -n '/^## Step 5: Final report/,/^## /p' "$PLUGIN/skills/autopilot/SKILL.md" | grep -q '/cost'; then
    pass "AC15 autopilot Step 5 final report includes the /cost summary line"
else
    bad "AC15 autopilot Step 5 final report has no /cost summary line"
fi

if [ "$fail" -eq 0 ]; then
    printf '\nRESULT: PASS\n'
else
    printf '\nRESULT: FAIL\n'
fi
exit "$fail"
