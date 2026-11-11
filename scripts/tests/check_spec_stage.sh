#!/usr/bin/env bash
# ABOUTME: Checks the /spec stage redesign: guardrails template, design step, stage labels.
# ABOUTME: Each check pins what /ready or a resumed session will parse, not prose wording.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PLUGIN="plugins/dev-jawn"
SPEC="$PLUGIN/skills/spec/SKILL.md"
TEMPLATE="$PLUGIN/skills/spec/assets/issue-template.md"
UIDESIGN="$PLUGIN/skills/ui-design/SKILL.md"
ARCH="$PLUGIN/skills/architecture/SKILL.md"
READY="$PLUGIN/skills/ready/SKILL.md"
LABELS="$PLUGIN/scripts/setup_labels.sh"
WORKFLOW="$PLUGIN/skills/WORKFLOW.md"
README="$PLUGIN/README.md"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }
check() { if eval "$2"; then pass "$1"; else bad "$1"; fi; }

# AC1 — template carries the sections /ready reads.
check "AC1a template has User Stories"   "grep -q '^## User Stories' '$TEMPLATE'"
check "AC1b template has Scenarios"      "grep -q '^## Scenarios' '$TEMPLATE'"
ac_section="$(awk '/^## Acceptance Criteria/{on=1;next} /^## /{on=0} on' "$TEMPLATE")"
check "AC1c acceptance criteria are Given/When/Then" \
      "echo \"\$ac_section\" | grep -q 'Given' && echo \"\$ac_section\" | grep -q 'When' && echo \"\$ac_section\" | grep -q 'Then'"
check "AC1d template has Guardrails"     "grep -q '^## Guardrails' '$TEMPLATE'"
for sub in 'Design constraints' 'Non-goals' 'Stop conditions' 'Rules'; do
    check "AC1d guardrails has $sub" "grep -q '^### $sub' '$TEMPLATE'"
done
check "AC1e template has design-checkpoint flag, default off" \
      "grep -qE 'design-checkpoint.*off' '$TEMPLATE'"
check "AC1e template has merge flag, default off" \
      "grep -qE '\`merge\`.*off' '$TEMPLATE'"

# AC2 — three entry paths.
check "AC2b spec documents design-only entry"   "grep -q '/spec #<issue_number> design' '$SPEC'"
check "AC2c spec documents re-spec entry"       "grep -qiE '^##+ Re-spec' '$SPEC'"
check "AC2c re-spec files nothing before approval" \
      "awk '/^##+ Re-spec/{on=1;next} /^## /{on=0} on' '$SPEC' | grep -qi 'files nothing'"

# AC3 — design runs /ui-design unattended; only design-checkpoint stops for the user.
design_step="$(awk '/^### Step [0-9]+: Design/{on=1;next} /^### /{on=0} on' "$SPEC")"
check "AC3 spec design step runs /ui-design"    "echo \"\$design_step\" | grep -q '/ui-design'"
check "AC3 spec design step names design-checkpoint" "grep -q 'design-checkpoint' '$SPEC'"
check "AC3 spec no longer invokes ux-designer as its own phase" "! grep -q 'Invoke the \`ux-designer\` skill' '$SPEC'"

# AC4 — /ui-design runs unattended with adversarial critics and a design log.
check "AC4a ui-design caps L at 4 passes"       "grep -qE 'effort/L[^0-9]+4 passes' '$UIDESIGN'"
check "AC4a ui-design caps S and M at 2 passes" "grep -qE 'effort/S.{0,20}effort/M[^0-9]+2 passes|effort/S and effort/M[^0-9]+2 passes' '$UIDESIGN'"
check "AC4b ui-design critics are adversarial"  "grep -qi 'adversarial' '$UIDESIGN'"
check "AC4c ui-design no per-pass approval"     "! grep -q 'You approve each pass' '$UIDESIGN'"
check "AC4d ui-design writes a design log"      "grep -qi 'design log' '$UIDESIGN'"

# AC5 — XL always splits.
check "AC5 spec never files an effort/XL issue" "grep -qi 'never file.\{0,30\}effort/XL' '$SPEC'"

# AC6 — /spec runs /ready itself; no /goal for the user to paste.
check "AC6 spec prints no /goal for /ready"     "! grep -q '^/goal Issue #<N> has been audited' '$SPEC'"
handoff="$(awk '/^### Step [0-9]+: Hand off to \/ready/{on=1;next} /^##/{on=0} on' "$SPEC")"
check "AC6 spec runs /ready at the end"         "echo \"\$handoff\" | grep -qi 'run \`/ready #'"

# AC10 — stage labels exist and /spec sets its own.
for st in spec design human ready architecture build review; do
    check "AC10 setup_labels defines stage:$st" "grep -q '\"stage:$st|' '$LABELS'"
done
for st in spec design human; do
    check "AC10 spec sets stage:$st" "grep -q 'stage:$st' '$SPEC'"
done
check "AC10 no stage:checkpoint remains" "! grep -rq 'stage:checkpoint' '$PLUGIN'"

# AC11 — resume never redoes the interactive requirements; needs-design is gone (the stage label says it).
check "AC11 stage:spec resume does not restart at Step 2" \
      "! grep -qE 'stage:spec. → resume at Step 2' '$SPEC'"
check "AC11 needs-design is gone from the plugin" "! grep -rq 'needs-design' '$PLUGIN'"

# AC12 — re-spec runs domain detection and every requirements step, so Sizing records the domain.
check "AC12 re-spec runs Steps 1 to 4" \
      "awk '/^##+ Re-spec/{on=1;next} /^## /{on=0} on' '$SPEC' | grep -q 'Run Steps 1 to 4'"

# AC13 — gaps get a proposed answer; big gaps stop the run and notify, small ones proceed as assumed.
step2="$(awk '/^### Step 2/{on=1;next} /^##+ /{on=0} on' "$SPEC")"
check "AC13a Step 2 gives every gap a proposed answer" "echo \"\$step2\" | grep -qi 'proposed answer'"
check "AC13b Step 2 no longer forbids filling gaps" "! tr '\\n' ' ' < '$SPEC' | grep -q 'Ask about each gap rather than filling it'"
check "AC13c big gaps are scope, money, privacy, security" \
      "echo \"\$step2\" | grep -i 'scope' | grep -i 'money' | grep -i 'privacy' | grep -qi 'security'"
check "AC13d a big gap with nobody to ask stops at stage:human" "echo \"\$step2\" | grep -q 'stage:human'"
check "AC13e stopped questions go in an issue comment" "echo \"\$step2\" | grep -q 'gh issue comment'"
check "AC13f a stop sends PushNotification"        "echo \"\$step2\" | grep -q 'PushNotification'"
check "AC13g template records small gaps as Assumptions" "grep -q '^## Assumptions' '$TEMPLATE'"
check "AC13h re-spec defers gaps to Step 2's rule" \
      "awk '/^##+ Re-spec/{on=1;next} /^## /{on=0} on' '$SPEC' | grep -q 'gap rule in Step 2'"

# AC14 — architecture is its own stage after /ready, not a /spec step.
check "AC14a setup_labels defines stage:architecture" "grep -q '\"stage:architecture|' '$LABELS'"
check "AC14a stage:architecture sits between ready and build" \
      "grep -o 'stage:[a-z]*|' '$LABELS' | tr -d '|' | tr '\\n' ' ' | grep -q 'stage:ready stage:architecture stage:build'"
check "AC14b spec invokes no architect" "! grep -qE 'Invoke \`[a-z-]*-architect\`' '$SPEC'"
check "AC14c architecture skill exists" "[ -f '$ARCH' ]"
check "AC14c architecture sets stage:architecture" "grep -q 'stage:architecture' '$ARCH' 2>/dev/null"
for a in swift-architect python-architect; do
    check "AC14c architecture names $a" "grep -q '$a' '$ARCH' 2>/dev/null"
done
check "AC14c architecture fills Technical Notes" "grep -q 'Technical Notes' '$ARCH' 2>/dev/null"
check "AC14d ready no longer routes to /spec for architecture" "! grep -q 'route to \`/spec\` for the architect phase' '$READY'"
check "AC14f architecture enters on stage:architecture" "grep -q 'Entry: \`stage:architecture\`' '$ARCH' 2>/dev/null"
check "AC14g spec repair reads ARCH VERDICT" "grep -q 'ARCH VERDICT' '$SPEC'"
check "AC14h architecture route-back swaps its own label" \
      "grep -q 'remove-label \"stage:architecture\" --add-label \"stage:spec\"' '$ARCH' 2>/dev/null"
check "AC14e ui-design no longer reads technical notes" "! grep -q 'technical notes (which views' '$UIDESIGN'"

# AC15 — the state machine: WORKFLOW.md lists every stage with its owner and next states, and
# each owning skill routes to exactly the next states its rows allow (both directions).
# Rows wrap; join each indented continuation line onto its row so one row is one line.
sm="$(awk '/^## State machine/{on=1;next} /^## /{on=0} on' "$WORKFLOW" \
      | awk '/^  [^ ]/ && prev!=""{sub(/^ +/," ");prev=prev $0;next} {if(prev!="")print prev; prev=$0} END{print prev}')"
check "AC15a WORKFLOW has a State machine section" "[ -n \"\$sm\" ]"
for st in $(grep -o '"stage:[a-z]*|' "$LABELS" | tr -d '"|'); do
    check "AC15b state machine lists $st" "echo \"\$sm\" | grep -q '^- \`$st\`:'"
done
owners="$(echo "$sm" | grep -o 'owner `/[a-z-]*`' | grep -o '/[a-z-]*' | sort -u)"
check "AC15c state machine names owner skills" "[ -n \"\$owners\" ]"
for o in $owners; do
    f="$PLUGIN/skills/${o#/}/SKILL.md"
    allowed="$(echo "$sm" | grep "owner \`$o\`" | grep -o 'next .*' | grep -o 'stage:[a-z]*' | sort -u)"
    owned="$(echo "$sm" | grep "owner \`$o\`" | grep -o '^- `stage:[a-z]*' | grep -o 'stage:[a-z]*')"
    routes="$(grep -o 'route=stage:[a-z]*' "$f" 2>/dev/null | cut -d= -f2 | sort -u)"
    for r in $routes; do
        check "AC15d $o routes to $r, which its rows allow" "echo \"\$allowed\" | grep -qx '$r'"
    done
    for a in $allowed; do
        check "AC15e $o sets $a, as its rows require" "echo \"\$routes\" | grep -qx '$a'"
    done
    for st in $owned; do
        check "AC15f $o checks entry on $st" "grep -q 'Entry:.*\`$st\`' '$f'"
    done
    check "AC15g $o points at the stage rules" "grep -q 'State machine' '$f'"
done
check "AC15h WORKFLOW states the verdict comment rule" "echo \"\$sm\" | grep -qi 'verdict comment'"
check "AC15i no label routes to /spec" "grep -qi 'no \`stage:\` label' '$SPEC'"

# AC16 — /spec chains the owners after filing until a human or the build is due.
handoff8="$(awk '/^### Step 8:/{on=1;next} /^##/{on=0} on' "$SPEC")"
check "AC16a Step 8 runs /architecture after /ready" "echo \"\$handoff8\" | grep -q '/architecture'"
check "AC16b Step 8 stops at stage:human or stage:build" \
      "echo \"\$handoff8\" | grep -q 'stage:human' && echo \"\$handoff8\" | grep -q 'stage:build'"
check "AC16c split children start at stage:spec" "! grep -q 'run Step 7 for each child' '$SPEC'"
check "AC16d /spec #N design resumes only stage:design" "grep -q '#N design.*stage:design' '$SPEC'"

# AC17 — chores and small bug fixes skip design, /ready and architecture.
for L in chore bug; do
    check "AC17a setup_labels defines $L" "grep -q '\"$L|' '$LABELS'"
    check "AC17b spec has a $L lane to stage:build" "grep -q 'kind=$L' '$SPEC'"
done
check "AC17c ui-design records a no-UI skip" "grep -qi 'no design needed' '$UIDESIGN'"

# AC18 — every route into stage:spec lands somewhere; no route loops.
repair="$(awk '/^## Repair Mode/{on=1;next} /^## /{on=0} on' "$SPEC")"
usage="$(awk '/^## Usage/{on=1;next} /^## /{on=0} on' "$SPEC")"
check "AC18a Repair reads a DESIGN VERDICT too" "echo \"\$repair\" | grep -q 'DESIGN VERDICT'"
check "AC18b /ready R4 passes findings the user accepted" \
      "awk '/^### R4/{on=1;next} /^### /{on=0} on' '$READY' | grep -qi 'accepted'"
check "AC18c split children carry a split-from verdict" "echo \"\$repair\" | grep -q 'split from #'"
check "AC18c mode detection sends split children to Re-spec" "echo \"\$usage\" | grep -q 'split from #'"
check "AC18d Repair with nobody to ask goes to stage:human" "echo \"\$repair\" | grep -q 'route=stage:human'"
check "AC18e mode detection is first match wins" "echo \"\$usage\" | grep -qi 'first match wins'"
check "AC18f stage:spec row allows stage:ready (repaired issue)" \
      "echo \"\$sm\" | grep '^- \`stage:spec\`' | grep -q 'stage:ready'"

# AC19 — /ready step 8 proves the acceptance test fails for the right reason.
step8="$(awk '/^8\. \*\*Check the test can fail/{on=1} /^The test will not pass yet/{on=0} on' "$READY")"
check "AC19a step 8 reads each failure line" "echo \"\$step8\" | grep -qi 'failure line'"
check "AC19b step 8 runs UI tests against the design prototype" "echo \"\$step8\" | grep -qi 'prototype'"
check "AC19c step 8 carries the stale-locator example" "echo \"\$step8\" | grep -q 'calsync #77'"

# AC20 — the build hands the issue to the user when the PR opens.
SUBMIT="$PLUGIN/skills/submit/SKILL.md"
check "AC20a submit posts a SUBMIT VERDICT routing to stage:human" "grep -q 'SUBMIT VERDICT: #<issue> route=stage:human' '$SUBMIT'"
check "AC20b submit swaps stage:build for stage:human" "grep -q 'stage:build. for .stage:human' '$SUBMIT'"
check "AC20c /spec stops on stage:human after a SUBMIT VERDICT" "echo \"\$usage\" | grep '^  - .stage:human' | grep -q 'SUBMIT VERDICT'"
check "AC20d WORKFLOW stage:human row names PR review" "echo \"\$sm\" | grep -A2 '^- \`stage:human\`' | grep -q 'SUBMIT VERDICT'"

# AC21 — a /submit re-entry re-runs the sweep only when non-test code changed.
step4="$(awk '/^### Step 4/{on=1;next} /^### /{on=0} on' "$SUBMIT")"
check "AC21 sweep re-runs only after a non-test change" "echo \"\$step4\" | grep -qi 'since the last green sweep'"

# AC22 — /architecture runs the domain architect skill instead of writing the notes itself.
check "AC22a architecture invokes the architect with the Skill tool" "grep -q 'Skill tool' '$ARCH'"
check "AC22b architecture forbids hand-written notes" "grep -qi 'not a substitute' '$ARCH'"
check "AC22c Technical Notes name the skill that filled them" "grep -q 'Filled by /architecture via' '$ARCH'"

# AC23 — design screenshots live in the repo under docs/design/<issue>/, pushed with the branch.
check "AC23a ui-design saves screenshots under docs/design/<issue>/" "grep -q 'docs/design/<issue>/' '$UIDESIGN'"
check "AC23b critics save captures there too, never the repo root" "grep -qi 'never the repo root' '$UIDESIGN'"
check "AC23c ui-design pushes the branch so the issue can link screenshots" "grep -q 'git push -u origin' '$UIDESIGN'"

# AC24 — deferred answers become linked follow-ups; a long criteria list prompts a split.
step4s="$(awk '/^### Step 4/{on=1;next} /^### Step 5/{on=0} on' "$SPEC")"
check "AC24a gap rule handles deferred answers" "echo \"\$step2\" | grep -q 'Deferred answers'"
check "AC24b deferred follow-up is listed under Non-goals" "echo \"\$step2\" | grep -A3 'Deferred answers' | grep -q 'Non-goals'"
check "AC24c sizing proposes a split past about 15 criteria" "echo \"\$step4s\" | grep -q 'about 15 criteria'"

# AC25 — the policy hook's /ready rule names the chore and bug lane.
HOOK="$PLUGIN/hooks/workflow-policy.sh"
check "AC25 hook lets chores and small bug fixes skip /ready" "grep 'Do NOT skip /ready' '$HOOK' | grep -q 'chores and small bug fixes'"

if [ "$fail" -eq 0 ]; then printf '\nRESULT: PASS\n'; else printf '\nRESULT: FAIL\n'; fi
exit "$fail"
