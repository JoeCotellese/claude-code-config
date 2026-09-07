#!/bin/bash
# ABOUTME: Acceptance test for issue #63 (/retro files upstream lessons as issues).
# ABOUTME: Checks the grep + frontmatter invariants that map to the issue's acceptance criteria; fails until shipped.

# Derived from #63 acceptance criteria at the Definition of Ready gate, before
# implementation. R7 is N/A for this repo (config repo, markdown work, exempt
# under the CLAUDE.md testing standard), so this script is not an AXe acceptance
# test; it is the named [test:] channel for AC1-AC6, AC8 and AC9. AC7 is
# [manual] and its automatable proxies are AC7a/AC7b below.
#
# The word measure is `wc -w` over the WHOLE file, frontmatter included. The
# implementer and this test must agree on that or the ceiling means nothing.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

SKILLS="plugins/dev-jawn/skills"
RETRO="$SKILLS/retro/SKILL.md"
PHASE_SKILLS="spec ready ui-design implement verify submit retro create-goal"

# Ceiling caps set at the Definition of Ready gate. A skill's declared max_words
# must be at or under its cap, so AC5 cannot be passed by declaring a ceiling
# large enough to fit anything. retro's cap budgets the Step 5 rewrite this
# issue performs (1,369 words today, ~450 added by the new scope decision,
# marketplace resolution, budget rule and inert-local flag, plus headroom).
cap_for() {
    case "$1" in
        create-goal) echo 1500 ;;
        implement)   echo 1750 ;;
        ready)       echo 4200 ;;
        retro)       echo 1900 ;;
        spec)        echo 2950 ;;
        submit)      echo 2150 ;;
        ui-design)   echo 1500 ;;
        verify)      echo 1700 ;;
        *)           echo 0 ;;
    esac
}

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

if [ ! -f "$RETRO" ]; then
    bad "retro/SKILL.md missing at $RETRO"
    printf '\nRESULT: FAIL — cannot run, retro skill absent.\n'
    exit 1
fi

# --- AC1 retro-no-hardcoded-config-path ------------------------------------
# The maintainer's clone path must not appear anywhere in the skill. The second
# pattern subsumes the first; both are checked because the issue names both.
hits=$(grep -c 'git/claude-code-config' "$RETRO" || true)
if [ "$hits" -eq 0 ]; then
    pass "AC1 retro-no-hardcoded-config-path: no git/claude-code-config in retro/SKILL.md"
else
    bad "AC1 retro-no-hardcoded-config-path: $hits occurrence(s) of git/claude-code-config remain"
    grep -n 'git/claude-code-config' "$RETRO" | sed 's/^/      /'
fi

# --- AC2 retro-does-not-branch ---------------------------------------------
# NOTE: at the gate, `git checkout -b` was present (:116) but a literal
# `git commit` was NOT. The issue claimed both; only one half failed. Both are
# asserted anyway so the rewrite cannot reintroduce either.
for pat in 'git checkout -b' 'git commit'; do
    if grep -q -- "$pat" "$RETRO"; then
        bad "AC2 retro-does-not-branch: '$pat' present in retro/SKILL.md"
        grep -n -- "$pat" "$RETRO" | sed 's/^/      /'
    else
        pass "AC2 retro-does-not-branch: no '$pat' in retro/SKILL.md"
    fi
done

# --- AC3 retro-files-issues-upstream ---------------------------------------
for pat in 'known_marketplaces.json' 'installed_plugins.json' 'gh issue create --repo'; do
    if grep -q -- "$pat" "$RETRO"; then
        pass "AC3 retro-files-issues-upstream: names '$pat'"
    else
        bad "AC3 retro-files-issues-upstream: does not name '$pat'"
    fi
done
# All three marketplace source kinds must be handled, because the dev-jawn
# marketplace itself is a `directory` source with no owner/repo in the JSON.
for pat in 'github' 'directory' 'remote get-url'; do
    if grep -q -- "$pat" "$RETRO"; then
        pass "AC3 retro-files-issues-upstream: handles source kind / resolution '$pat'"
    else
        bad "AC3 retro-files-issues-upstream: no handling for '$pat'"
    fi
done
# The never-edit-the-source rule must survive, including for local directories.
if grep -qi 'never edit the plugin source' "$RETRO"; then
    pass "AC3 retro-files-issues-upstream: states the never-edit-plugin-source rule"
else
    bad "AC3 retro-files-issues-upstream: missing the never-edit-plugin-source rule"
fi

# --- AC4 retro-line-carries-scope ------------------------------------------
if grep -q 'status=proposed' "$RETRO"; then
    bad "AC4 retro-line-carries-scope: status=proposed still present"
else
    pass "AC4 retro-line-carries-scope: no status=proposed"
fi
if grep -q 'amendment=' "$RETRO"; then
    bad "AC4 retro-line-carries-scope: amendment= field still present"
else
    pass "AC4 retro-line-carries-scope: no amendment= field"
fi
for v in 'scope=local' 'scope=upstream' 'scope=none'; do
    if grep -q -- "$v" "$RETRO"; then
        pass "AC4 retro-line-carries-scope: documents $v"
    else
        bad "AC4 retro-line-carries-scope: missing $v"
    fi
done
if grep -q 'dest=' "$RETRO"; then
    pass "AC4 retro-line-carries-scope: RETRO line carries dest="
else
    bad "AC4 retro-line-carries-scope: no dest= field"
fi

# --- AC5 skills-declare-max-words ------------------------------------------
for s in $PHASE_SKILLS; do
    f="$SKILLS/$s/SKILL.md"
    cap=$(cap_for "$s")
    if [ ! -f "$f" ]; then bad "AC5 skills-declare-max-words: $s/SKILL.md missing"; continue; fi
    # max_words must be in the frontmatter block, not merely somewhere in prose.
    declared=$(awk 'NR==1 && $0!="---"{exit} NR>1 && $0=="---"{exit} /^max_words:[[:space:]]*[0-9]+/{print $2}' "$f")
    if [ -z "$declared" ]; then
        bad "AC5 skills-declare-max-words: $s declares no max_words in frontmatter"
        continue
    fi
    actual=$(wc -w < "$f" | tr -d ' ')
    if [ "$declared" -gt "$cap" ]; then
        bad "AC5 skills-declare-max-words: $s declared $declared exceeds gate cap $cap"
    elif [ "$actual" -gt "$declared" ]; then
        bad "AC5 skills-declare-max-words: $s is $actual words, over its declared $declared"
    else
        pass "AC5 skills-declare-max-words: $s $actual/$declared (cap $cap)"
    fi
done

# --- AC6 retro-states-budget-rule ------------------------------------------
# The three permitted outcomes must sit WITH the ceiling rule, not merely appear
# somewhere in the file. A bare `grep -qi replace` over the whole skill would go
# green on an unrelated sentence, so the window is the ceiling paragraph +/- 8 lines.
WINDOW=$(grep -n -i -e 'ceiling' -e 'max_words' "$RETRO" >/dev/null 2>&1 \
    && grep -i -B8 -A8 -e 'ceiling' -e 'max_words' "$RETRO" || echo "")
if [ -z "$WINDOW" ]; then
    bad "AC6 retro-states-budget-rule: retro/SKILL.md never mentions a ceiling or max_words"
else
    b_replace=0; b_local=0; b_consolidate=0
    printf '%s' "$WINDOW" | grep -qi 'replac'      && b_replace=1
    printf '%s' "$WINDOW" | grep -qi 'local'       && b_local=1
    printf '%s' "$WINDOW" | grep -qi 'consolidat'  && b_consolidate=1
    if [ $b_replace -eq 1 ] && [ $b_local -eq 1 ] && [ $b_consolidate -eq 1 ]; then
        pass "AC6 retro-states-budget-rule: ceiling rule names replace / stay local / consolidate"
    else
        bad "AC6 retro-states-budget-rule: near the ceiling rule replace=$b_replace local=$b_local consolidate=$b_consolidate"
    fi
fi

# --- AC7 proxies (the criterion itself is [manual]) ------------------------
# AC7a: the rewrite cannot pass by accretion. Covered by AC5's retro row, but
# asserted here too so a reader lining up criteria finds AC7 represented.
retro_words=$(wc -w < "$RETRO" | tr -d ' ')
retro_cap=$(cap_for retro)
if [ "$retro_words" -le "$retro_cap" ]; then
    pass "AC7a proxy: retro/SKILL.md $retro_words words, at or under gate cap $retro_cap"
else
    bad "AC7a proxy: retro/SKILL.md $retro_words words, over gate cap $retro_cap"
fi
# AC7b: one decision procedure, not two. The scope branch must enumerate exactly
# the three RETRO scope values and no fourth, and no second landing procedure
# may remain (a `### Step 5` followed by another landing heading).
scope_values=$(grep -o 'scope=[a-z]*' "$RETRO" | sort -u | wc -l | tr -d ' ')
if [ "$scope_values" -eq 3 ]; then
    pass "AC7b proxy: exactly 3 distinct scope= values documented"
else
    bad "AC7b proxy: $scope_values distinct scope= values documented, expected 3"
    grep -o 'scope=[a-z]*' "$RETRO" | sort -u | sed 's/^/      /'
fi
if grep -qi 'Land the amendment in the right repository' "$RETRO"; then
    bad "AC7b proxy: the old 'Land the amendment in the right repository' procedure remains"
else
    pass "AC7b proxy: old landing procedure heading is gone"
fi

# --- AC8 retro-flags-inert-local -------------------------------------------
if grep -qi 'inert\|not yet enforced\|until the gates read' "$RETRO" && grep -q '#64' "$RETRO"; then
    pass "AC8 retro-flags-inert-local: states local amendments are inert and names #64"
else
    bad "AC8 retro-flags-inert-local: missing the inert statement or the #64 reference"
fi

# --- AC9 retro-handles-unresolved-upstream ---------------------------------
# ADDED AT THE GATE (see the /ready audit comment on #63). The issue's procedure
# has no branch for a marketplace whose owning repository cannot be resolved.
if grep -q 'dest=unresolved' "$RETRO"; then
    pass "AC9 retro-handles-unresolved-upstream: documents dest=unresolved"
else
    bad "AC9 retro-handles-unresolved-upstream: no dest=unresolved fallback documented"
fi

# --- Dependencies section must not promise config-repo write access --------
if grep -q 'Write access to the config repo' "$RETRO"; then
    bad "AC1 retro-no-hardcoded-config-path: Dependencies still claims config-repo write access"
else
    pass "AC1 retro-no-hardcoded-config-path: Dependencies no longer claims config-repo write access"
fi

printf '\n'
if [ "$fail" -eq 0 ]; then
    printf 'RESULT: PASS — #63 shell invariants hold.\n'
    printf 'AC7 is [manual]: read Step 5 end to end and confirm it is one decision\n'
    printf 'procedure, not two bolted together. The proxies above cannot judge that.\n'
else
    printf 'RESULT: FAIL — #63 not shipped (expected before implementation).\n'
fi
exit "$fail"
