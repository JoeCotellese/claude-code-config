#!/usr/bin/env bash
# ABOUTME: Acceptance checks for #137: /spec dispatches design, ready and architecture to fresh subagents.
# ABOUTME: Pins the rules a /spec run follows in Steps 7 and 8; AC10 (peak context) is measured on the pilot run.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PLUGIN="plugins/dev-jawn"
SPEC="$PLUGIN/skills/spec/SKILL.md"
UIDESIGN="$PLUGIN/skills/ui-design/SKILL.md"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }
check() { if eval "$2"; then pass "$1"; else bad "$1"; fi; }

# Steps 7 and 8 plus anything inserted before Re-spec Mode (a dispatch subsection counts).
hand="$(awk '/^### Step 7:/{on=1} /^## Re-spec Mode/{on=0} on' "$SPEC")"
step8="$(awk '/^### Step 8:/{on=1;next} /^##/{on=0} on' "$SPEC")"

# AC1 — each later phase runs in a fresh general-purpose subagent, never a fork.
check "AC1a dispatch names subagent_type general-purpose" "echo \"\$hand\" | grep -q 'general-purpose'"
check "AC1b dispatch forbids fork" "echo \"\$hand\" | grep -iqE '(never|not|no)[^.]*fork'"
check "AC1c Step 7 hands /ui-design to the subagent" \
      "awk '/^### Step 7:/{on=1;next} /^### /{on=0} on' '$SPEC' | grep -iq 'subagent'"

# AC2 — the hand-back is the verdict line, links and blocking items, capped.
check "AC2a hand-back is capped at 150 words" "echo \"\$hand\" | grep -q '150 words'"
check "AC2b hand-back carries the verdict line" "echo \"\$hand\" | grep -iq 'verdict line'"

# AC3 — the next owner comes from the label on GitHub, not the hand-back.
check "AC3 Step 8 re-reads labels from GitHub" "echo \"\$step8\" | grep -q 'json labels'"

# AC4 — existing stop rules survive.
check "AC4a Step 8 stops at stage:human or stage:build" \
      "echo \"\$step8\" | grep -q 'stage:human' && echo \"\$step8\" | grep -q 'stage:build'"
check "AC4b second route back to stage:spec sets stage:human" \
      "echo \"\$step8\" | grep -iq 'second route back'"

# AC5 — a phase that leaves the label unchanged stops the run, no retry.
check "AC5a unchanged label routes to stage:human" \
      "echo \"\$step8\" | grep -iE 'unchanged|still (the|at)' | grep -q 'stage:human'"
check "AC5b no re-dispatch" "echo \"\$step8\" | grep -iqE 'no retry|not re-?dispatch|never re-?dispatch'"

# AC6 — no Playwright in the subagent: stop at stage:human, never fall back inline.
check "AC6a ui-design stops at stage:human when Playwright is unavailable" \
      "grep -iE 'playwright[^.]*(unavailable|cannot|can.t)|(unavailable|cannot|can.t)[^.]*playwright' '$UIDESIGN' | grep -q 'stage:human'"
check "AC6b /spec never runs a phase inline" "echo \"\$hand\" | grep -iqE '(never|not|no)[^.]*inline'"

# AC7 — Repair stays in the main session.
check "AC7 stage:spec runs in this session" \
      "echo \"\$step8\" | grep '\`stage:spec\`' | grep -iqE '(this|main) session'"

# AC8 — a phase hands back only after its own subagents report.
check "AC8 dispatch waits for the phase's own subagents" \
      "echo \"\$hand\" | grep -iE 'wait' | grep -iqE 'critic|architect|subagent'"

# AC9 — /spec itself notifies on a stage:human stop.
check "AC9 Step 8 calls PushNotification" "echo \"\$step8\" | grep -q 'PushNotification'"

# AC11 — the word ceiling holds.
words=$(wc -w < "$SPEC" | tr -d ' ')
check "AC11 spec/SKILL.md is at or under 3000 words ($words)" "[ $words -le 3000 ]"

exit $fail
