---
name: ready
effort: high
description: "Definition of Ready gate. Invoke with `/ready #<issue>` or when the user says 'is this ready', 'DoR check', 'audit this issue', 'can we implement #N'. Audits an issue against seven readiness criteria, repairs what it can (rewrites vague acceptance criteria, names accessibility identifiers, derives the acceptance test), and routes what it cannot back to /spec or /ui-design. Prints a fixed DOR VERDICT line so a /goal evaluator can judge the outcome."
---

# Definition of Ready Gate

Sits between `/spec` and the build phases. An issue that has not passed `/ready` does not get
implemented.

```
/spec  →  /ready  →  /ui-design  →  /implement  →  /submit
            │ ▲          │
            ▼ │          ▼
          /spec      (missing design routes here)
```

This phase **repairs before it rejects**. Most issues fail the Definition of Ready on things
that can be fixed by rewriting: vague acceptance criteria, unnamed accessibility identifiers,
a missing acceptance test. Fix those in place and amend the issue. Route back only what needs
a human decision: missing requirements, unbounded scope, absent design.

## Usage

```
/ready #<issue_number>
```

Designed to run unattended under a goal. Print this for the user rather than setting it
yourself:

```
/goal Issue #<N> has been audited by /ready and the transcript contains a line beginning
"DOR VERDICT: #<N>" whose status is PASS, or whose route is /spec or /ui-design with the
blocking criteria named. Report the route and stop. Stop after 6 turns.
```

## The Seven Criteria

Audit each one. A criterion is PASS, FAIL, or N/A. Record the evidence, not just the verdict.

### R1 — User stories exist

At least one story in role/action/benefit form, each carrying acceptance criteria.

- PASS: "As a cook, I want to ask Siri about my recipe box so that I can find a recipe
  without unlocking my phone", followed by criteria.
- FAIL: a title and a paragraph of technical description with no stated user.

**Repairable.** Derive stories from the issue's description and the app's existing patterns.
Post them for the record. If the issue does not say who benefits or why, that is not
repairable: route to `/spec`.

### R2 — Acceptance criteria are observable

This is the criterion that makes the Definition of Done possible. Every AC must name a UI
element or an app state that a test can assert against.

- PASS: "Tapping `saveRecipeButton` on a recipe already saved shows `recipeAlreadySavedToast`
  and does not create a duplicate."
- FAIL: "Saving feels fast." "The flow is intuitive." "Errors are handled gracefully."

**Every AC must also name the channel that observes it.** "Observable in principle" is not
enough: an AC about internal behavior can be perfectly precise and still have nothing watching
it. Each AC carries one of three tags:

- **`[ui]`** — asserted by the AXe acceptance test through an accessibility identifier.
- **`[test: <name>]`** — asserted by a named unit or integration test. Use this for behavior
  with no UI surface: a migration running exactly once, a write path touching only one record,
  an attribute set having the right shape.
- **`[manual]`** — verified by a human, with the reason automation cannot. Allowed, but an AC
  tagged `[manual]` must be paired with an automatable proxy that catches regressions. "Reads
  naturally under VoiceOver" is genuinely manual; "`contentDescription` contains no newlines
  and is under two sentences" is the proxy that guards it between manual checks.

An untagged AC fails R2 even when its wording is precise. This is the most common way an issue
looks ready and is not: the criteria are crisp, nothing observes half of them, and the gap
surfaces at the end when the DoD test is written and covers three of five criteria.

Rewrite each failing AC into observable form. Preserve the intent: "feels fast" usually means
a stated latency budget, "handled gracefully" usually means a named error state. When you
cannot tell what the author meant, say so in the verdict and route to `/spec` rather than
inventing a requirement.

**Repairable in most cases.**

### R3 — Identifier contract

Every element referenced by an AC has a named `accessibilityIdentifier`. Without this, the
acceptance test in R7 cannot address anything.

Check the codebase for identifiers that already exist before inventing new ones:

```bash
rg -o 'accessibilityIdentifier\("([^"]+)"\)' -r '$1' --no-filename | sort -u
```

Reuse an existing identifier when the element already ships. Name new ones in the same style
as their neighbors (this codebase uses lowerCamelCase, for example `settingsNavigationLink`,
`spotlightSearchToggle`, `recipeList`).

Write the contract into the issue as a list of identifier and element pairs. `/implement` is
bound by it: a view that ships without these identifiers fails its own DoD test.

**Repairable.**

### R4 — Design artifact

User-facing work needs approved screens that meet Apple HIG and fit the app's existing
aesthetic.

- PASS: the issue links or embeds approved screens, or carries a `design::readyforeng` label.
- FAIL for a UI feature: UX marked "provisional — pending design" by `/spec`, or absent.
- N/A: backend, CLI, or infrastructure work with no user-visible surface.

**Not repairable here.** Route to `/ui-design`. This is a forward route, not a rejection: the
rest of the audit still runs and its repairs still land, so `/ui-design` starts from a clean
issue.

### R5 — Technical approach

An implementer can start without re-deriving the architecture. Look for the types and files to
touch, the data flow, and decisions already made with their rationale.

- PASS: names the concrete symbols and files, states the decisions and why.
- FAIL: "use the existing service layer" with no indication which service or what changes.

Verify the named symbols actually exist. A technical approach that references a type that was
renamed six months ago is worse than none, because it sends the implementer down a dead end.

**Partially repairable.** You can look up and correct stale symbol names. You cannot invent an
architecture: route to `/spec` for the architect phase.

### R6 — Bounded scope

An `effort/` label is present and is not XL.

Also check for the conflation pattern: an issue that lists several capabilities each with
independent shipping value is XL regardless of its label. Say which sub-issues it should
become.

**Not repairable.** Route to `/spec` to split.

### R7 — Acceptance test exists

An acceptance test in the project's own harness whose `success_criteria` map one-to-one onto
the R2 acceptance criteria. On Apple platforms that is an AXe YAML under `scripts/uitests/`;
on web it is a named Playwright flow. The procedure below is written for the AXe case, which
is the one with the most moving parts; the rules hold for either harness.

**Derive it here, before any code exists.** That ordering is the point: it forces the ACs to
be testable and it gives `/implement` a target that was not written by the person trying to
pass it.

Procedure:

1. Read `~/.claude/skills/ios-ui-tester/SKILL.md` for the harness and
   `assets/test-template.yaml` for the schema.
2. Read two or three existing tests in `scripts/uitests/` to match local conventions.
3. Write `scripts/uitests/test_<slug>.yaml`. Start with the two-line `ABOUTME:` header the
   other tests carry.
4. Every `[ui]` AC from R2 becomes exactly one entry under `success_criteria`. Same order, same
   wording where possible. A reader must be able to line them up without interpretation.
   `[test:]` and `[manual]` criteria do not belong in the AXe file; list them in the issue
   under the DoD section so nothing is silently dropped. Every AC must be covered by exactly
   one channel, and the count has to reconcile: if the issue has nine criteria and the AXe file
   has five, the other four are named somewhere or the audit is wrong.
5. Steps reference the R3 identifiers by `element_id`. Do not use raw coordinates for elements
   that will have identifiers, because those tests break on every layout change.
6. Cover the empty, typical, and stress states the ACs describe, not just the happy path.
7. **Check the trigger is reachable.** A criterion can be perfectly observable and still have
   no way to reach the state that exhibits it. Siri invocation is not drivable in a simulator;
   a push notification path needs a way to fire one; a migration needs a way to install the
   prior version's state. Before declaring R7 satisfied, name the concrete command or gesture
   that puts the app into each asserted state. If none exists, say what has to be built to make
   it reachable and add it to the issue as an implementation task, flagged as added for
   testability so the user can object. An entry point that already exists and is extended is
   fine; a test-only backdoor that bypasses the real code path is not, because it passes while
   the feature is broken.

The test will not pass yet. Nothing is built. That is expected and correct: it is the failing
test at the top of the TDD cycle, one level up.

For non-UI work, R7 is satisfied by naming the unit or integration test targets instead, with
the same one-to-one mapping to the ACs.

**Repairable.** This is the main artifact `/ready` produces.

## Workflow

### Step 1 — Fetch the issue

```bash
glab issue view $ISSUE_NUM                       # GitLab (ClipDish default)
gh issue view $ISSUE_NUM --json title,body,labels  # GitHub
```

Record: title, body, labels, and whether an `effort/` label is present.

### Step 2 — Classify

- **User-facing?** Look for a `UI` label, or ACs that describe screens and taps. Determines
  whether R4 applies and whether R7 is an AXe test or a unit test list.
- **Size gate.** Read the `effort/` label and record which committee tier later phases get.
  S gets one reviewer, M gets two, L gets three. Write the tier into the issue so `/ui-design`
  and `/submit` do not re-derive it.

### Step 3 — Audit and repair

Work R1 through R7 in order. Later criteria depend on earlier ones: R7 cannot be written
until R2 is observable and R3 is named.

For each criterion, capture one line of evidence: what you found, quoted or cited, not a
summary. The verdict has to be defensible when the user disagrees with it.

**Stop repairing once an unrepairable criterion fails.** R7 depends on R2 and R3, and all of
them depend on R6: if the scope is wrong, the acceptance criteria belong to issues that do not
exist yet, and every repair you make is thrown away when the issue is split. So when R6 fails,
or when R1 or R5 fail unrepairably, finish the *audit* on the remaining criteria and report
what they would need, but do not write the repairs and do not derive the acceptance test.
Say so in the verdict.

Audit all seven regardless. A verdict that stops at the first failure tells the user one thing
to fix, then wastes another round discovering the next.

### Step 4 — Branch and commit the artifacts

`/ready` is the first phase that writes to the repo, so it creates the branch. Never commit
to main.

```bash
EXISTING=$(git branch -a | grep -E "(feature|fix)/${ISSUE_NUM}-" | head -1 | xargs)
if [ -n "$EXISTING" ]; then
    git checkout "$EXISTING"
else
    bash ~/.claude/skills/implement/scripts/create_feature_branch.sh $ISSUE_NUM feature <brief-desc>
fi
```

Commit the acceptance test:

```
Test #<N>: Add acceptance test for <feature>

Derived from the issue's acceptance criteria at the Definition of Ready gate,
before implementation. Fails until the feature ships.
```

`/ui-design` and `/implement` continue on this branch.

### Step 5 — Amend the issue

Post the repairs back so the issue becomes the artifact of record:

- Rewritten user stories and observable acceptance criteria
- The accessibility identifier contract
- The path to the committed acceptance test
- The committee tier from the size gate
- Any criterion that routed out, with what specifically is missing

Post as an edit when replacing content, as a comment when adding an audit trail. Do not
silently overwrite something a human wrote: quote what you replaced.

### Step 6 — Print the verdict

**Exactly this format, on its own line.** The goal evaluator reads it and it is the only thing
it can see:

```
DOR VERDICT: #347  status=FAIL  passed=5/7  blocking=R4,R6  route=/spec
```

- `status` — PASS only when every applicable criterion passes. N/A counts as passing.
- `passed` — count over applicable criteria.
- `blocking` — the criteria that failed, comma separated, or `none`.
- `route` — the single next phase.

Routing rules, first match wins:

1. R6 fails, or R1/R5 fail unrepairably → `route=/spec`
2. R4 fails (design missing) → `route=/ui-design`
3. Everything applicable passes, feature has UI, design present → `route=/ui-design`
4. Everything applicable passes, no UI → `route=/implement`

Then print the criterion-by-criterion table as a list, and the `/goal` command for the routed
phase so the user can paste it.

## Success Condition

The issue on the remote now contains observable acceptance criteria and an identifier
contract, an acceptance test derived from those criteria is committed on the feature branch,
and a `DOR VERDICT:` line names the route. If a run produces a verdict but no committed test
and no issue amendment, the gate did not do its job.

## What this skill must not do

- **Do not invent requirements.** When the issue does not say what should happen, route to
  `/spec`. A confidently fabricated acceptance criterion is worse than a blocked issue,
  because it passes DoR and gets built.
- **Do not weaken an acceptance criterion to make it observable.** "Search returns results
  ranked by relevance" does not become "search returns results." Say it needs a definition of
  relevance and route out.
- **Do not skip R7 because the feature is hard to test.** If the acceptance criteria cannot be
  expressed as a test, they are not acceptance criteria, and the issue is not ready.

## Dependencies

- `glab` (ClipDish default) or `gh`
- `ios-ui-tester` skill for the AXe test schema and conventions
- `~/.claude/skills/implement/scripts/create_feature_branch.sh` for branch naming

## Next Phase

Whatever `route=` says. `/spec` to fix the specification, `/ui-design` to design it,
`/implement` to build it. `/implement` closes with `/verify`, which runs the test committed
here and prints the `DOD VERDICT` line that answers this gate.

When a criterion fails in a way that means an earlier phase should have caught it, that is a
`/retro`, not just a reroute.
