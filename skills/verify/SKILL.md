---
name: verify
effort: medium
description: "Definition of Done runner. Invoke with `/verify #<issue>` or when the user says 'run the DoD', 'is this done', 'check acceptance', 'did it pass'. Runs the unit suite and the acceptance test authored at /ready against the built app, reconciles every acceptance criterion to the channel that observes it, writes a results file, and prints a fixed DOD VERDICT line so a /goal evaluator can judge the outcome. Runs inside /implement's goal loop or standalone."
---

# Definition of Done Runner

Closes the loop `/ready` opened. `/ready` wrote the acceptance test before any code existed;
`/verify` runs it against what was built and prints a verdict a goal evaluator can read.

```
/ready  →  /implement  →  /verify  →  /submit
             ▲              │
             └──────────────┘
                FAIL routes back
```

This skill **runs and reports. It does not fix.** A `/verify` run that edits product code to
make its own test pass has destroyed the only objective signal in the loop. When something
fails, print the verdict and route back to `/implement`.

## Usage

```
/verify #<issue_number>
/verify                    # infers the issue from the branch name
```

Normally called inside `/implement`'s goal loop. Standalone use is fine: run the DoD on demand
against any branch that has an acceptance test.

## The Definition of Done

All three hold:

1. **The unit suite is green.** Zero failures. Pristine output — a suite that passes while
   printing unexpected errors is a FAIL, per the project's testing standard.
2. **The acceptance test passes.** The harness test `/ready` committed runs against the built
   app and every `success_criteria` entry is met.
3. **Every acceptance criterion is accounted for.** Each AC in the issue reconciles to the
   channel that observed it: `[ui]` to an acceptance-test criterion, `[test: <name>]` to a
   named test that actually ran, `[manual]` to a human's recorded answer. An AC with nothing
   reporting on it is a FAIL, not a skip. This is the check that catches a green suite that
   simply never exercised half the feature.

Caveats do not lower the bar. A run may report `PASS (with caveats)` only when every criterion
passed and the caveat is about the *run* (a flaky simulator boot, a retried step), never about
a criterion that went unobserved.

## Workflow

### Step 1 — Resolve the issue and the DoD contract

```bash
ISSUE_NUM="${1:-$(git branch --show-current | grep -oE '[0-9]+' | head -1)}"
glab issue view $ISSUE_NUM                          # GitLab (ClipDish default)
gh issue view $ISSUE_NUM --json title,body,labels   # GitHub
```

Extract, from the sections `/ready` wrote:

- Every acceptance criterion with its channel tag.
- The path to the committed acceptance test.
- The identifier contract, so a missing `accessibilityIdentifier` is reported as the contract
  violation it is rather than as a mysterious element-not-found.
- The `[manual]` criteria and their automatable proxies.

If the issue has no channel tags or no acceptance test, the issue never passed `/ready`. Stop
and say so: `route=/ready`. Do not invent a Definition of Done at the end of the cycle, which
is exactly the failure the gate exists to prevent.

### Step 2 — Detect the platform

```bash
DOMAIN=$(bash ~/.claude/skills/submit/scripts/detect_project_domain.sh)
```

Always run the script. Do not guess from context. The domain picks both commands below.

- **`swift`** — unit: `swift test` (or `xcodebuild test` for an app target). Acceptance: AXe
  YAML under `scripts/uitests/`, driven by the `ios-ui-tester` skill.
- **`python`** — unit: `pytest`. Acceptance: the Playwright flow named by the issue for a web
  UI; for non-UI work the named integration tests are the acceptance channel.
- **`cpp-qt`** — unit: `ctest --test-dir build`. Acceptance: the project's GUI test target if
  one exists; otherwise the `[ui]` criteria are `[manual]` and must carry proxies, which is a
  `/ready` question, not a `/verify` one.
- **`unknown`** — STOP and ask which harness to run. Do not fall back to "run the tests I can
  find" and report a verdict on it.

### Step 3 — Run the unit suite

Run it first. It is cheaper than the acceptance harness and its failures are more diagnostic.

Capture the failure count and the output. **If the suite fails, still run the acceptance
harness** unless the build itself is broken. One `/verify` run that reports both failures
saves a round trip over two runs that each report one.

### Step 4 — Run the acceptance harness

For `swift`, read `~/.claude/skills/ios-ui-tester/SKILL.md` and follow it, including the
checkpoint screenshots. The AX tree proves an element is present, not that the screen
rendered.

For every domain, the rules are the same:

- Run the test `/ready` committed. Do not rewrite it to match what was built. A test that
  needed changing is a finding, reported in the verdict, and the change is `/ready`'s to make
  after a `/retro`, not yours.
- Record each `success_criteria` entry as met or not met, with the evidence.
- A step that cannot execute (element absent, state unreachable) is a **FAIL**, never a skip.

### Step 5 — Run the named `[test: …]` criteria

For each `[test: <name>]` AC, confirm that test exists and ran in Step 3. A named test that is
missing from the suite is a FAIL against that criterion: the AC was assigned a channel and the
channel was never built.

### Step 6 — Collect the `[manual]` criteria

These cannot be run. List them for the user with their proxies, and record the proxy's result
(the proxy is automatable by definition, so it has one). Ask for a yes/no on each manual
criterion. Unanswered manual criteria make the status FAIL, because the verdict has to be
defensible.

### Step 7 — Reconcile

Count. The issue's criteria total must equal the sum of criteria observed across the three
channels. If nine ACs produced seven results, name the two that went unobserved and fail.

### Step 8 — Write the results file

```
{project}/scripts/uitests/results/YYYY-MM-DD_HHMM_<name>.md
```

Contents: date, issue number, branch, commit SHA, status, the unit summary, a
criterion-by-criterion table as a list with evidence, the checkpoint screenshot directory,
and any workarounds or unexpected element positions.

Commit it. The results file is the durable record of what "done" meant on this issue.

### Step 9 — Print the verdict

**Exactly this format, on its own line.** The goal evaluator does not call tools; this line
and the lines under it are all it can see:

```
DOD VERDICT: #347  status=FAIL  criteria=7/9  unit=1-failing  acceptance=FAIL  results=scripts/uitests/results/2026-08-02_0930_spotlight.md  route=/implement
```

- `status` — PASS, FAIL, or `PASS-with-caveats`. PASS only when all three parts of the
  Definition of Done hold.
- `criteria` — criteria observed and passing over criteria in the issue.
- `unit` — `green` or `<n>-failing`.
- `acceptance` — PASS, FAIL, or `n/a` for work with no `[ui]` criteria.
- `results` — repo-relative path to the file from Step 8.
- `route` — the single next phase.

Routing rules, first match wins:

1. The issue has no acceptance test or no channel tags → `route=/ready`
2. The acceptance test had to be wrong to fail (it asserts something the ACs never said, or
   its trigger is unreachable) → `route=/retro`
3. Any criterion failed → `route=/implement`
4. Everything passed → `route=/submit`

Then print the criterion-by-criterion list. Route 2 is the one that needs judgment: a failing
test is presumed right and the code presumed wrong. Only route to `/retro` when you can quote
the AC and the assertion and show they disagree.

## Running under a goal

`/implement` sets the goal that wraps this skill. When run standalone, print this rather than
setting it yourself:

```
/goal Issue #<N> has been verified and the transcript contains a line beginning
"DOD VERDICT: #<N>" whose status is PASS or PASS-with-caveats, or whose route names the
phase that owns the failure. Report the route and stop. Stop after 4 turns.
```

## Success Condition

A results file is committed, every acceptance criterion in the issue appears in it with an
outcome and evidence, and a `DOD VERDICT:` line names the route. A run that prints a verdict
with no results file did not verify anything.

## What this skill must not do

- **Do not edit product code.** Not to fix a failure, not to add a missing identifier. Report
  it and route to `/implement`.
- **Do not edit the acceptance test to make it pass.** That is the one move that turns the
  whole loop into theatre.
- **Do not report PASS on an unobserved criterion.** Unobserved is FAIL. "Probably fine" is
  not a channel.
- **Do not re-derive acceptance criteria from the code.** They come from the issue. If the
  code does something the issue never asked for, that is a finding.

## Dependencies

- `glab` (ClipDish default) or `gh`
- `~/.claude/skills/submit/scripts/detect_project_domain.sh` for platform detection
- `ios-ui-tester` skill for the AXe harness on `swift` projects
- Playwright MCP for web acceptance flows

## Next Phase

Whatever `route=` says. `/submit` on a pass, `/implement` on a code failure, `/retro` when the
gate that should have caught it upstream did not.
