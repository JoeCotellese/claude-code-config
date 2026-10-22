# Finding Triage

How `/submit` Step 3 decides which committee findings block a submission, and how it fixes the
ones that do. A finding blocks only when a test proves it: a plausible-but-unreachable finding
should not halt a submission the way a real crash does, and no fix should land without a test
that was red first.

## Scope

In scope:

1. `/code-review` findings with `category: correctness`. Every other `/code-review` category
   (simplification, efficiency, and the rest) is non-blocking: log it to the issue and drop it.
2. Lens B (platform safety) findings that Lens B marks blocking. Its non-blocking findings are
   logged to the issue and dropped.

Lens A and Lens C are out of scope and keep their own handling. Lens A is covered by the
acceptance test, and Lens C's findings are about the tests themselves, so a reproduction test
would be grading the thing under review. A blocking finding from either one STOPs the
submission as Step 3 describes.

## Step 1: Assign a severity

Read the finding's `failure_scenario` (and its `CONFIRMED`/`PLAUSIBLE` verdict, if present)
and the code it names, then assign one severity:

1. **S1**: crash, data loss, security, or wrong output on a normal path.
2. **S2**: wrong output on an edge path reachable from real input.
3. **S3**: theoretical, unreachable from current callers, or style posing as a bug.

S3 findings are not fixed. Log each to the issue with one line on why it is unreachable, then
drop it. When the call between S2 and S3 is close, pick S2: the reproduction test settles it.

Lens B reviewers (`swift-swiftui-reviewer`, `python-code-reviewer`, `cpp-qt-reviewer`) do not
return `ReportFindings`, so their findings have no `failure_scenario` field. State one from the
finding's description first, in the same shape: concrete inputs or state, then the wrong output
or crash. A Lens B finding you cannot state a failure scenario for is S3.

## Step 2: Reproduce S1 and S2 before any fix

For each S1 and S2 finding, write a test from its `failure_scenario` and run it on the unfixed
branch. Use the project's single-test command so the run covers that test only. This happens
before any fix, for every in-scope finding, so the result reflects the code as reviewed.

1. **Test fails**: the finding is confirmed and blocking. Keep the test; it is the red step of
   the fix loop.
2. **Test passes**: a test that passes on the unfixed branch marks a false positive.
   The failure does not happen. Log it to the issue as a false positive (with the scenario you
   tested), drop it, and delete the test. A test that never failed guards nothing.

**Escape hatch.** An S1 that cannot be expressed as a test stops and asks the user how to proceed.
Races, main-actor violations, and transient UI state are the usual cases. It is never dropped silently, and it
is never reclassified as S3 to get past this gate. An S2 that cannot be expressed as a test is
logged to the issue as unconfirmed and dropped.

## Step 3: Fix loop

`/submit` runs the fixes itself, in severity order: S1 before S2. For each confirmed finding:

1. Red: the reproduction test from Step 2 fails.
2. Fix: the minimal change that addresses the failure scenario. Nothing else.
3. Green: the reproduction test passes.
4. Commit the test and the fix together.

That is red, fix, green, one finding at a time. After the last confirmed finding is green, do the
scoped Step 4 rerun from `SKILL.md` (build plus the tests covering the touched files), not the
full suite unless Step 4 says so.

If a fix reveals a gap the Definition of Ready should have caught, that is also a `/retro`.

## Reporting

Record every in-scope finding's outcome for the PR's Testing section:

1. Confirmed findings fixed, each with its severity and the name of its reproduction test.
2. False positives dropped, each with one line on the scenario that did not reproduce.
3. S3 findings logged and dropped.
