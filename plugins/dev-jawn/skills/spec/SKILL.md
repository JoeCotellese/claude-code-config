---
name: spec
max_words: 2950
effort: xhigh
description: "Specification phase: requirements and design. Invoke with `/spec <feature description>` to create an issue, `/spec #<issue>` to resume or re-spec one, `/spec #<issue> design` to run only the design step, or after /ready routes an issue back. Also triggers on 'new feature', 'plan feature', 'create spec', 'split this issue', 'fix issue #N', 'design #N'. Writes user stories, scenarios, Given/When/Then acceptance criteria and guardrails with the user, then runs the next owners unattended: /ui-design, /ready, /architecture."
---

# Specification Phase

The spec is everything an unattended build needs: requirements **and** design. The human
writes the requirements and guardrails here; the design step and `/ready` then run on their
own. Requirements and design can happen in one session or separate ones.

```
/spec: requirements + guardrails (with the user) → /ui-design → /ready → /architecture (unattended)
```

Entry: `stage:spec` or `stage:human`, or an issue with no `stage:` label. As the driver
(Step 8) it also runs the owners of `stage:design`, `stage:ready` and `stage:architecture`.
Labels, verdict comments and the last-action rule follow State machine in `WORKFLOW.md`.

## Usage

```
/spec <brief feature description>    # create
/spec #<issue_number>                # resume from the stage label, or re-spec
/spec #<issue_number> design         # design step only
```

**Mode detection:**

- Plain text → **Create**.
- `#N design` → only on an issue at stage:design: run `/ui-design #N`, then Step 8.
- `#N` → read the issue's `stage:` label and the latest verdict comment. First match wins:
  - `stage:build` → stop: the build run owns it.
  - `stage:human` → after a `SUBMIT VERDICT`, stop: the PR awaits review. Otherwise the
    latest verdict says what waits on the user. Ask it, then post their
    decision as `SPEC VERDICT` with the return state it names (`route=stage:spec`,
    `route=stage:design` or `route=stage:ready`), set that label, and go to Step 8.
  - `stage:design`, `stage:ready`, `stage:architecture` → Step 8.
  - The latest verdict says `split from #<P>` → **Re-spec**: the child's own pass.
  - The latest verdict has `route=stage:spec` and names what blocks → **Repair**.
  - No `stage:` label, or a feature body lacking the template's Scenarios, Given/When/Then
    or Guardrails sections → **Re-spec**.
  - `stage:spec` with a filed body → Step 7.

When the argument is ambiguous, ask rather than guess: a duplicate issue is a mess to unwind.

**Also triggers on:**
- Create: "new feature X", "plan feature X", "create spec for X", "I have an idea for X"
- Repair: "split issue #N", "fix the spec for #N", "#N failed DoR"
- Design: "design #N", "prototype #N"

## Workflow Overview

Create mode:

```
Step 1:    Detect domain           (automatic)
Step 2:    Requirements            (with the user)
Step 3:    Guardrails + flags      (with the user)
Step 4:    Sizing + gate           (with the user)
Step 5:    GATE                    ← "File this spec?"
Step 6:    Create issue            (automatic, stage:spec)
Step 7:    Design                  (unattended, UI features only)
Step 8:    Hand off to /ready      (unattended)
```

## Workflow Steps

### Step 1: Detect Project Domain

```bash
DOMAIN=$(bash ${CLAUDE_PLUGIN_ROOT}/skills/submit/scripts/detect_project_domain.sh)
```

It prints `swift`, `python`, `cpp-qt`, `ambiguous:<a>,<b>`, or `unknown`. On `ambiguous`, ask which
stack the feature targets. Record it under Sizing for `/architecture`.

### Step 2: Requirements

**Chores and small bug fixes** skip stories, scenarios and design. Decide the kind first; ask
when unsure, and treat it as a feature when nobody can answer.

- **Chore** (`chore` label): no behavior change: formatting, lint, deletions, renames, a
  dependency bump with no API change. One criterion that is a command, e.g. "`ruff format
  --check .` exits 0". The `merge` flag is on.
- **Bug fix** (`bug` label): restores intended behavior, `effort/S`, changes no screen and
  needs no design or architecture decision. One Given/When/Then that reproduces it; the build
  writes it as a failing test first. `merge` stays off. Anything bigger is a feature.

Both still get guardrails, sizing and the gate, then Step 7 routes them to `stage:build`.

For a feature, invoke the `product-manager` skill.

**Prompt the skill with:**
```
Define product requirements for: <user's feature description>

Produce:
- User stories: As a <role>, I want <capability>, so that <outcome>
- Scenarios: one short narrative per path a user takes, including unhappy paths
- Acceptance criteria as Given/When/Then, one per criterion
- Success metrics and analytics events
- Accessibility requirements (tier level)
- Edge cases and error states

Output format: Feature brief (not full PRD unless complex)
```

**Every Then must be observable by a command or test.** It names an app state, a stored
record, a response, or a message a test can assert against. This is what lets `/ready` turn
the criteria into the goal an unattended build runs against; a criterion nothing can check
means the issue can never be Done.

- Observable: "Given a recipe already saved, when the user saves it again, then no duplicate
  is stored and an already-saved message is shown."
- Not observable: "Saving feels fast." "The flow is intuitive." "Errors are handled
  gracefully."

**Keep the Then behavioral, not visual.** The design does not exist yet; Step 7 names the
screens and accessibility identifiers. A Then that names a pixel or a layout is design work
done too early.

Keep acceptance criteria separate from implementation tasks. "Conforms to `AppEntity`" is a
task: it can be completed while the feature does not work. Put tasks under their own heading.

**Gap rule.** Act as the product manager: break each story past its happy path (forgot
password, wrong input, no permission, empty state) and list every gap with a proposed answer.
Ask in one round, for example "Wrong password 5 times: lock for 15 minutes. Accept?" Each
confirmed answer becomes a criterion. A guess never becomes a criterion unconfirmed.

Sort each gap before asking:

- **Big:** it changes scope, or touches money, privacy, or security.
- **Small:** everything else, such as a count, a timeout, or a default.

When nobody can answer (an unattended run, or the user does not reply):

- Small gaps proceed on the proposed answer, listed under the issue's `## Assumptions`.
- Any big gap stops the run. Post the big gaps with their proposed answers via
  `gh issue comment` as `SPEC VERDICT: #N route=stage:human` naming `stage:spec` as the return
  state, set `stage:human`, and call `PushNotification` with the
  issue and the count, e.g. "/spec stopped on #77: 2 scope questions need you." Resume when
  the user answers.

**Collect output as:** `PM_OUTPUT`

### Step 3: Guardrails and Flags

The guardrails are what lets the design and build run without the user. Draft each from the
requirements and the codebase, then confirm with the user:

- **Design constraints** — platform, the house components or design system to use, and what
  the design must not invent (new screens, navigation, dependencies).
- **Non-goals** — what this issue deliberately leaves unbuilt, so no critic or reviewer
  treats it as a gap.
- **Stop conditions** — what makes an unattended run halt and report instead of finishing.
  Always include: a criterion cannot be met without changing the spec.
- **Rules** — what a run must never do: weaken an assertion, touch protected files, add a
  dependency.

Then the two flags, both **off by default**. Use AskUserQuestion only when the feature
suggests one should be on:

- `design-checkpoint` — the design step stops for the user's look before `/ready`. Turn on
  when design risk is high: a new flow, a screen users see daily, a taste call.
- `merge` — the build run merges its own PR. Turn on for chores and deletions.

**Collect output as:** `GUARDRAILS`, `FLAGS`

### Step 4: Value/Effort Sizing

Assess the feature on two dimensions using the labels available in the repo. Use
AskUserQuestion to confirm sizing with the user.

**Value** — business impact to users or the product:
| Rating | Meaning |
|--------|---------|
| S | Nice-to-have, minor polish |
| M | Useful improvement, affects some users |
| L | Important feature, clear user demand |

Value tops out at L. There is no `value/XL`: a critical capability is still `value/L`.

**Effort** — implementation complexity. It also caps the design step's passes:
| Rating | Meaning | Design passes |
|--------|---------|---------------|
| S | 1-2 files, clear scope, < 1 hour | 2 |
| M | Multiple files, some investigation needed | 2 |
| L | Cross-cutting, multi-service, needs design | 4 |
| XL | Epic-level, should be broken into sub-issues | split |

**XL always splits.** Never file an `effort/XL` issue: an unattended run that the user only
judges at the end throws away the most work when rejected. Go to [Split](#step-r3a-split)
with this spec as the parent, size each child S to L, and run Steps 6 to 9 per child.

Present the proposed sizing with a one-line rationale each:
```
**Value: <proposed>** — <one-line rationale>
**Effort: <proposed>** — <one-line rationale>

Does this sizing look right?
- Yes
- Adjust value
- Adjust effort
- Adjust both
```

**Collect confirmed sizing as:** `VALUE_SIZE`, `EFFORT_SIZE`, `VALUE_RATIONALE`, `EFFORT_RATIONALE`

#### Gate classification — who closes it

Value and effort are the priority axis. The gate is a second axis: **who can close this
issue, and can an unattended loop touch it.** Every issue gets exactly one `gate:` label, and
`/ready` refuses to pass an issue whose gate is unset (Definition of Ready, R8).

| Gate | Meaning |
|--------|---------|
| `gate:machine` | An unattended loop can drive it to done — no person, no hardware, no external approval in the close path. |
| `gate:human` | A person or physical hardware must close it: a device test, a taste call, a credential only a human holds. |
| `gate:mixed` | Both — a machine does most of it, but at least one step needs a human. |

Ask honestly: "could a loop finish this with no me and no device?" When in doubt it is
`gate:mixed`: an over-eager `gate:machine` lets an autonomous puller grab something it cannot
finish. Confirm with AskUserQuestion. **Collect as:** `GATE_CLASS`.

`unattended` and `blocked` are set by `/ready`; `/spec` sets only `gate:` and `stage:`.

### Step 5: GATE — File This Spec?

Compose the body from `assets/issue-template.md`. Show the user Layer 1 per Phase closeout
in `${CLAUDE_PLUGIN_ROOT}/skills/WORKFLOW.md`: what the feature lets a user do, its size, its
flags, and the criteria count. Then AskUserQuestion:

```
File #<title> and start design?
- Yes (Recommended) → file, then design and /ready run unattended
- Tell me more → Layer 2
- Refine spec → adjust first
- Stop here → I'll pick it up later
```

Continue only on an explicit yes.

### Step 6: Create Issue

Detect the platform from `git remote get-url origin` (`github`, `gitlab`, else unknown).

**For GitHub:**
```bash
gh issue create \
  --title "Feature: <brief title>" \
  --label "value/<VALUE_SIZE>" \
  --label "effort/<EFFORT_SIZE>" \
  --label "gate:<GATE_CLASS>" \
  --label "stage:spec" \
  --body "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

Add `--label chore` or `--label bug` for those kinds.

**For GitLab:** the same with `glab issue create` and `--description`.

**Unknown platform:** output the body and recommended labels for manual creation, and stop.

If a label is missing, run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup_labels.sh` once, then retry.

### Step 7: Design

Post `SPEC VERDICT: #N route=stage:design blocking=none` with what was filed, then swap
`stage:spec` for `stage:design`. A chore posts `SPEC VERDICT: #N route=stage:build kind=chore`
(a bug fix `kind=bug`), sets `stage:build`, and stops: the build run is not built yet.

Run `/ui-design #<N>` (skill `ui-design`) for every feature. It decides whether there is UI to
design and records "no design needed" when there is none; otherwise it runs the critic loop
and posts the design log. **Do not stop between passes or after them.** The user judges the
design at the end, through the log and the screenshots.

The one exception is the `design-checkpoint` flag. When set, `/ui-design` sets `stage:human`
and stops for the user's look.

### Step 8: Hand off to /ready

Do not ask. In this session, keep running the owner of the issue's label until it reaches
`stage:human` or `stage:build`:

- `stage:design` → `/ui-design #<N>`
- `stage:ready` → run `/ready #<N>` (skill `ready`): are requirements and design sufficient?
- `stage:architecture` → `/architecture #<N>` (skill `architecture`)
- `stage:spec` → Mode detection again (usually Repair). A second route back to `stage:spec`
  in one run sets `stage:human` instead, so the loop cannot spin.

Report per Phase closeout: the issue link, the design log link, and the last verdict's route.

## Re-spec Mode

Invoked as `/spec #<issue>` on an issue written before this template: no Scenarios, no
Given/When/Then, or no Guardrails. Typical for existing backlogs and epics.

1. Read the issue, its comments, and the parent epic if one exists. Epic decisions and
   technical notes are shared context: copy what applies into each child.
2. Run Steps 1 to 4 against the existing body (Sizing records Step 1's domain), carrying over every requirement and decision
   it states. Convert each existing criterion into Given/When/Then; one that cannot be
   converted without inventing intent is a gap, handled by the gap rule in Step 2.
3. Write each proposed body to the scratchpad, one file per issue, and show the user a
   summary of what changed per section. **Re-spec files nothing** to the tracker until the
   user approves.
4. On approval, post the old body verbatim as a comment titled "Issue body before re-spec on
   <date>", replace the body, set `stage:spec`, then continue at Step 7.

## Repair Mode

Invoked as `/spec #<issue>`, normally because `/ready` printed a verdict routing here.

### Step R1: Read the verdict

Find the latest `DOR VERDICT`, `ARCH VERDICT`, `DESIGN VERDICT`, or the user's `SPEC VERDICT`.
What it blocks on determines the repair. If none names a blocker, set `stage:ready` and go to
Step 8 rather than guess.

### Step R2: Pick the repair

| Blocking | Repair | What it does |
|----------|--------|--------------|
| R6 scope | **Split** | Break one issue into independently shippable children |
| R1 stories | **Fill** | Re-run the PM step against the existing issue |
| R2 ambiguous | **Clarify** | Ask the user the specific questions, then amend |
| A contradiction (ARCH, DESIGN) or the user's spec change | **Clarify** | Settle how the spec changes, then amend |

More than one can apply. Split first: filling before splitting fills issues about to be
dissolved.

**Nobody to ask** (the split gate, Clarify): post `SPEC VERDICT: #<N> route=stage:human` with
the question and `stage:spec` as the return state, set `stage:human`, and stop, as in Step 2.

### Step R3a: Split

**Find the seams.** A child is a genuine child when it passes both tests:

- **Ships alone.** It delivers user value on its own, without waiting for a sibling.
- **Owns its criteria.** Its acceptance criteria are about it, not shared with a sibling.

Content that fails both is shared context: duplicate it into every child that needs it.
Children must be readable without opening the parent.

**Gate before creating anything.** Creating several issues is outward-facing and tedious to
unwind. Use AskUserQuestion to present the proposed split first:

```
#<N> splits into <count> issues:

1. <title> — <one line on what ships> — effort/<S|M|L>
2. <title> — <one line on what ships> — effort/<S|M|L>

Dependency order: <which must land first, and why>

- Create them → I'll file the children and convert #<N> into an epic
- Adjust the split → tell me what to merge or separate
- Stop → leave #<N> as it is
```

**Preserve the original.** Before rewriting the parent body, post it verbatim as a comment
titled "Original issue body before split on <date>". Never destroy something a human wrote.

**Create each child** from the template, with its own stories, scenarios, Given/When/Then,
guardrails, flags, value and effort labels, `stage:spec`, and a link back to the parent, and
post `SPEC VERDICT: #<child> route=stage:spec blocking=none split from #<N>` on it.

**Convert the parent** into an epic: an overview, the child list in dependency order, the
shared context, and the `epic` label. Keep the parent's References section.

### Step R3b: Fill

Re-invoke the step that produced the missing content, giving it the existing issue as
context:

- R1 missing stories → `product-manager` skill

**Verify before you amend.** A note that cites `RecipeSearch.swift:65` is only
useful if that line still says what the issue claims. Correct stale citations: a confidently
wrong file reference sends the implementer somewhere real and wrong.

Amend the issue in place, quoting whatever you replaced.

### Step R3c: Clarify

Reached when acceptance criteria are too ambiguous to rewrite without inventing requirements.
Rewriting "saving feels fast" as "saves within 2 seconds" is inventing, not repairing.

Use AskUserQuestion with the specific ambiguities, one question per genuine fork. Amend the
issue with the answers and note that they came from the user.

### Step R4: Hand back to /ready

Every repaired issue re-enters through the gate that rejected it. A repair is not
self-certifying. Print, for each issue that came out of the repair:

```
REPAIR COMPLETE: #<N>  action=<split|fill|clarify>  produced=<issue numbers>  route=stage:ready
```

Children start at `stage:spec`; their `split from #<N>` verdict sends each through its own
Re-spec pass, which can split it again. Run Step 8 on each child in dependency order. A repaired issue goes to `stage:ready` (a stale design sends it on to
`stage:design`), then Step 8, without asking.

## Error Handling

- **No git remote:** Output issue content for manual creation
- **CLI not authenticated:** Provide `gh auth login` or `glab auth login` instructions
- **Skill unavailable:** Skip that step with a note, continue with available steps

## Dependencies

- `product-manager` skill (requirements)
- `ui-design` skill (design step)
- `ready` skill (handoff)
- `gh` or `glab` CLI

## Next Phase

Step 8 chains the stages to `stage:build` or `stage:human`. Only chores and small bug fixes
skip `/ready`.
