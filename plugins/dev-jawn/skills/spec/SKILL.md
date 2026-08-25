---
name: spec
effort: xhigh
description: "Feature specification phase. Invoke with `/spec <feature description>` to create an issue, or `/spec #<issue>` to repair one that failed the /ready Definition of Ready gate. Also triggers on 'new feature', 'plan feature', 'create spec', 'split this issue', 'fix issue #N'. Orchestrates product management, UX design, and architecture planning. Hands off to /ready."
---

# Feature Specification Phase

Two modes, one skill.

- **Create** — turn an idea into a well-formed issue.
- **Repair** — take an issue that failed the Definition of Ready and fix what `/ready` could
  not fix itself.

Repair mode is the loop's reverse edge. Without it a `DOR VERDICT` of `route=/spec` is a dead
end that a human has to clear by hand.

## Usage

```
/spec <brief feature description>    # create
/spec #<issue_number>                # repair
```

**Examples:**
```
/spec Add a recipe sharing feature with social integration
/spec #347
```

**Mode detection:** an argument that is a bare number or starts with `#` is repair mode.
Anything else is create mode. When it is ambiguous, ask rather than guess: creating a
duplicate issue for something that already exists is a mess to unwind.

**Also triggers on:**
- Create: "new feature X", "plan feature X", "create spec for X", "I have an idea for X"
- Repair: "split issue #N", "fix the spec for #N", "#N failed DoR"

## Workflow Overview

Create mode:

```
Step 1-3:  PM → UX           (automatic)
Step 4:    GATE              ← "Ready for architecture?"
Step 5:    Arch              (automatic)
Step 6:    Sizing            (automatic)
Step 7-9:  Issue creation    (automatic)
Step 10:   GATE              ← "Ready for /ready?"
```

Repair mode: see [Repair Mode](#repair-mode) below.

## Workflow Steps

Execute these steps sequentially. Steps flow automatically EXCEPT at gates (Steps 4 and 10) where you MUST stop and ask the user.

### Step 1: Detect Project Domain

Analyze the codebase to determine the primary technology:

```bash
# Check for Swift/iOS project
if ls *.xcodeproj >/dev/null 2>&1 || ls *.xcworkspace >/dev/null 2>&1; then
    DOMAIN="swift"
# Check for Python
elif ls *.py >/dev/null 2>&1 || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    DOMAIN="python"
else
    DOMAIN="unknown"
fi
echo "$DOMAIN"
```

Store the result for architect selection in Step 4.

### Step 2: Product Requirements (PM Phase)

Invoke the `product-manager` skill to define requirements.

**Prompt the skill with:**
```
Define product requirements for: <user's feature description>

Focus on:
- User stories with acceptance criteria
- Success metrics and analytics events
- Accessibility requirements (tier level)
- Edge cases and error states

Output format: Feature brief (not full PRD unless complex)
```

**Every acceptance criterion must be observable.** It names a UI element or an app state that
a test can assert against. This is criterion R2 of the Definition of Ready, and an issue that
fails it cannot have an acceptance test written for it, which means it can never be Done.

- Observable: "Tapping `saveRecipeButton` on an already-saved recipe shows
  `recipeAlreadySavedToast` and does not create a duplicate."
- Not observable: "Saving feels fast." "The flow is intuitive." "Errors are handled
  gracefully."

Keep acceptance criteria separate from implementation tasks. "Conforms to `AppEntity`" and
"change `static var` to `static let`" are tasks: they can all be completed while the feature
does not work. Put them under their own heading so nobody mistakes checking them off for
being done.

**Collect output as:** `PM_OUTPUT`

### Step 3: UX Design (Designer Phase)

Invoke the `ux-designer` skill.

**Prompt:**
```
Review and provide UX guidance for this feature:

<user's feature description>

Context from PM:
<PM_OUTPUT summary - key user flows only>

Provide:
- Platform-specific design guidelines compliance
- Navigation and interaction patterns
- Accessibility UX requirements
- Visual hierarchy recommendations
```

**Name the accessibility identifier for every element an acceptance criterion references.**
This is criterion R3 of the Definition of Ready. Without it the acceptance test has nothing to
address, and `/ready` has to invent names later with less context than you have now.

Check what already exists before inventing:

```bash
rg -o 'accessibilityIdentifier\("([^"]+)"\)' -r '$1' --no-filename --glob '*.swift' | sort -u
```

Reuse an identifier when the element already ships. Name new ones in the local style
(lowerCamelCase in this codebase: `settingsNavigationLink`, `recipeList`,
`spotlightSearchToggle`). Output them as a list of identifier and element pairs.

**Collect output as:** `UX_OUTPUT`

### Step 4: GATE - Review Requirements & UX

**CRITICAL**: STOP and ask user before proceeding to architecture.

Use the AskUserQuestion tool to prompt:
```
Requirements and UX design complete.

**PM Requirements:** <brief summary>
**UX Guidance:** <brief summary>

Ready to proceed to architecture design?
- Yes → Continue to architecture phase
- Refine requirements → Let's adjust the PM requirements
- Refine UX → Let's adjust the UX design
```

**DO NOT continue to architecture until user explicitly confirms.**

### Step 5: Architecture (Architect Phase)

Select architect based on DOMAIN from Step 1 (detected earlier):

| Domain | Architect |
|--------|-----------|
| swift | Invoke `swift-architect` skill |
| python | Invoke `python-architect` skill |
| unknown | Ask user to specify, or provide generic guidance |

**Prompt the architect with:**
```
Design architecture for: <user's feature description>

PM Requirements:
<PM_OUTPUT summary>

UX Constraints:
<UX_OUTPUT summary>

Provide:
- Component diagram (ASCII)
- Data flow
- File structure
- Key implementation decisions
```

**Collect output as:** `ARCH_OUTPUT`

**After architecture is complete, AUTOMATICALLY proceed to sizing.**

### Step 6: Value/Effort Sizing

Assess the feature on two dimensions using the labels available in the repo. Use AskUserQuestion to confirm sizing with the user.

**Value** — business impact to users or the product:
| Rating | Meaning |
|--------|---------|
| S | Nice-to-have, minor polish |
| M | Useful improvement, affects some users |
| L | Important feature, clear user demand |

Value tops out at L. There is no `value/XL`: a critical capability is still `value/L`, and the
thing that actually needs its own tier is effort, where `XL` triggers a split back to `/spec`.

**Effort** — implementation complexity:
| Rating | Meaning |
|--------|---------|
| S | 1-2 files, clear scope, < 1 hour |
| M | Multiple files, some investigation needed |
| L | Cross-cutting, multi-service, needs design |
| XL | Epic-level, should be broken into sub-issues |

Present the proposed sizing to the user with brief rationale for each. Use the AskUserQuestion tool:
```
Based on the requirements and architecture:

**Value: <proposed>** — <one-line rationale>
**Effort: <proposed>** — <one-line rationale>

Does this sizing look right?
- Yes
- Adjust value
- Adjust effort
- Adjust both
```

**Collect confirmed sizing as:** `VALUE_SIZE`, `EFFORT_SIZE`, `VALUE_RATIONALE`, `EFFORT_RATIONALE`

**Then classify the gate before creating the issue.**

#### Gate classification — who closes it

Value and effort are the priority axis. The gate is a second, orthogonal axis: **who can close
this issue, and can an unattended loop touch it.** Every issue gets exactly one `gate:` label,
and `/ready` refuses to pass an issue whose gate is unset (Definition of Ready, R8).

| Gate | Meaning |
|--------|---------|
| `gate:machine` | An unattended loop can drive it to done — no person, no hardware, no external approval in the close path. |
| `gate:human` | A person or physical hardware must close it: a device test, a taste call, a credential only a human holds. |
| `gate:mixed` | Both — a machine does most of it, but at least one step needs a human. |

Ask for the machine-closability honestly: "could a loop finish this with no me and no device?"
When in doubt it is `gate:mixed`, not `gate:machine` — an over-eager `gate:machine` is what lets
an autonomous puller grab something it cannot actually finish.

Confirm with AskUserQuestion:
```
Gate — who closes #<N>?
**Proposed: gate:<machine|human|mixed>** — <one-line rationale>

- Yes
- gate:machine  (loop can finish it)
- gate:human    (needs a person or hardware)
- gate:mixed    (both)
```

**Collect confirmed gate as:** `GATE_CLASS`.

The other routing labels — `unattended` (safe for the loop to pull with no human/hardware),
`blocked` (cannot proceed yet), `needs-design` (must go through `/ui-design` first) — are set by
`/ready` and the design phase, not here. `/spec` sets only `gate:`.

**Then AUTOMATICALLY proceed to create the issue.**

### Step 7: Detect Git Platform

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$REMOTE_URL" | grep -qi "github"; then
    PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qi "gitlab"; then
    PLATFORM="gitlab"
else
    PLATFORM="unknown"
fi
echo "$PLATFORM"
```

### Step 8: Create Issue

Compose the issue from collected outputs, using the template in `assets/issue-template.md`.

**For GitHub:**
```bash
gh issue create \
  --title "Feature: <brief title from feature description>" \
  --label "value/<VALUE_SIZE>" \
  --label "effort/<EFFORT_SIZE>" \
  --label "gate:<GATE_CLASS>" \
  --body "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For GitLab:**
```bash
glab issue create \
  --title "Feature: <brief title from feature description>" \
  --label "value/<VALUE_SIZE>" \
  --label "effort/<EFFORT_SIZE>" \
  --label "gate:<GATE_CLASS>" \
  --description "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For unknown platform:** Output the composed issue to the user for manual creation, noting the recommended labels.

### Step 9: Report Success

Return to user:
- Issue URL (if created)
- Issue number (e.g., #123)
- Summary of what was planned
- Value/Effort sizing applied

**Then IMMEDIATELY proceed to Step 10 (the final gate).**

### Step 10: GATE - Ready for Next Phase

**CRITICAL**: STOP and ask user before proceeding.

**The next phase is always `/ready`**, whether or not the feature has a UI. `/ready` audits the
issue against the Definition of Ready, derives the acceptance test, and routes to `/ui-design`
or `/implement` from there. Do not route around the gate: a spec you just wrote is exactly the
kind that looks ready to the person who wrote it.

When the feature has a UI, mark the issue's UX and acceptance sections **provisional — pending
design**, since `/ui-design` will finalize them. `/ready` reads that marker and routes
accordingly.

Use the AskUserQuestion tool to prompt:
```
✅ Spec complete!

Issue: #<issue_number>
URL: <issue_url>

Next is the Definition of Ready gate, which will derive the acceptance test.
- Yes → Continue to /ready #<issue_number>
- Refine spec → Let's adjust first
- Stop here → I'll pick it up later
```

**DO NOT invoke the next phase until the user explicitly confirms "Yes".**

**When user confirms "Yes":** print the `/goal` command for the user to paste, rather than
invoking the skill directly. `/ready` is designed to run unattended and the goal is what makes
that work:

```
/goal Issue #<N> has been audited by /ready and the transcript contains a line beginning
"DOR VERDICT: #<N>" whose status is PASS, or whose route is /spec or /ui-design with the
blocking criteria named. Report the route and stop. Stop after 6 turns.
```

## Repair Mode

Invoked as `/spec #<issue>`, normally because `/ready` printed a verdict routing here.

### Step R1: Read the verdict

Find the most recent `DOR VERDICT:` line for this issue, in the conversation or in the issue's
comments. It names the blocking criteria, which determines the repair.

If no verdict exists, run `/ready #<issue>` first. Do not guess at what is wrong with an issue
someone asked you to repair; the audit is cheap and the guess is expensive.

### Step R2: Pick the repair

| Blocking | Repair | What it does |
|----------|--------|--------------|
| R6 scope | **Split** | Break one issue into independently shippable children |
| R1 stories, R5 approach | **Fill** | Re-run the PM or architect phase against the existing issue |
| R2 ambiguous | **Clarify** | Ask the user the specific questions, then amend |

More than one can apply. Split first: it changes which content belongs to which issue, so
filling before splitting means filling issues that are about to be dissolved.

### Step R3a: Split

**Find the seams.** A child is a genuine child when it passes both tests:

- **Ships alone.** It delivers user value on its own, without waiting for a sibling.
- **Owns its criteria.** Its acceptance criteria are about it, not shared with a sibling.

Content that fails both tests is not a child, it is shared context, and it gets duplicated
into every child that needs it. Children must be readable without opening the parent.

**Gate before creating anything.** Creating several issues is outward-facing and tedious to
unwind. Use AskUserQuestion to present the proposed split first:

```
#<N> splits into <count> issues:

1. <title> — <one line on what ships> — effort/<S|M|L>
2. <title> — <one line on what ships> — effort/<S|M|L>
...

Dependency order: <which must land first, and why>

- Create them → I'll file the children and convert #<N> into an epic
- Adjust the split → tell me what to merge or separate
- Stop → leave #<N> as it is
```

**Preserve the original.** Before rewriting the parent body, post it verbatim as a comment
titled "Original issue body before split on <date>". Never destroy something a human wrote.
The split is a judgment call and judgment calls get revisited.

**Create each child** carrying its own overview, user stories with observable acceptance
criteria, the slice of UX and architecture that applies to it, its own value and effort
labels, and a link back to the parent. Size each child independently: the parent's `effort/M`
does not mean each child is M.

**Convert the parent** into an epic: an overview, the child list in dependency order, the
shared context children reference, and the `epic` label. Keep the parent's References section.

### Step R3b: Fill

Re-invoke the phase that produced the missing content, giving it the existing issue as
context rather than starting from a blank page:

- R1 missing stories → `product-manager` skill
- R5 missing or stale technical approach → the domain architect skill

**Verify before you amend.** A technical approach that cites `RecipeSearch.swift:65` is only
useful if that line still says what the issue claims. Check the citations and correct the
stale ones. A confidently wrong file reference is worse than none, because it sends the
implementer somewhere real and wrong.

Amend the issue in place, quoting whatever you replaced.

### Step R3c: Clarify

Reached when acceptance criteria are too ambiguous to rewrite without inventing requirements.
That distinction matters: rewriting "saving feels fast" as "saves within 2 seconds" is
inventing a requirement, not repairing one.

Use AskUserQuestion with the specific ambiguities, not a general request for more detail. One
question per genuine fork, with the options you can see. Then amend the issue with the answers
and note that they came from the user.

### Step R4: Hand back to /ready

Every repaired issue re-enters the loop through the gate that rejected it. A repair is not
self-certifying.

Print, for each issue that came out of the repair:

```
REPAIR COMPLETE: #<N>  action=<split|fill|clarify>  produced=<issue numbers>  route=/ready
```

Then print the `/goal` command for the user to paste:

```
/goal Each of issues <list> has been audited by /ready and the transcript contains a
"DOR VERDICT:" line for each one. Report each verdict and its route, then stop.
Stop after <2 × count> turns.
```

## Output Composition

The issue should be scannable with clear sections:
1. **Overview** - One paragraph summary
2. **User Stories** - From PM phase
3. **UX Design** - From designer phase
4. **Architecture** - From architect phase
5. **Acceptance Criteria** - Consolidated checklist
6. **Analytics Events** - From PM phase
7. **Sizing** - Value/Effort ratings with rationale

## Error Handling

- **No git remote:** Output issue content for manual creation
- **CLI not authenticated:** Provide `gh auth login` or `glab auth login` instructions
- **Domain unknown:** Ask user to specify or provide generic architecture
- **Skill unavailable:** Skip that phase with a note, continue with available phases

## Dependencies

This skill orchestrates:
- `product-manager` skill (for PM phase)
- `ux-designer` skill (for design phase)
- `swift-architect`, `cpp-qt-architect`, or `python-architect` skill (for architecture)
- `gh` CLI (for GitHub issues)
- `glab` CLI (for GitLab issues)

## Next Phase

Both modes hand off to → `/ready`, which audits the Definition of Ready and routes onward to
`/ui-design` or `/implement`. Nothing skips the gate, including issues this skill just wrote.
