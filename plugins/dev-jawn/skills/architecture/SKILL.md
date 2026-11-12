---
name: architecture
max_words: 800
effort: high
description: "Architecture stage: decides how to build an issue labeled stage:architecture, which /ready sets on a pass. Invoke with `/architecture #<issue>` or when the user says 'architect #N', 'technical design for #N'. Runs the domain architect against the stories, guardrails and design, fills the issue's Technical Notes, and routes back to /spec when the code contradicts the spec."
---

<!-- ABOUTME: Architecture stage of dev-jawn: runs after /ready, before the build. -->
<!-- ABOUTME: Fills the issue's Technical Notes from the domain architect skill. -->

# Architecture

Entry: `stage:architecture`, which `/ready` sets when an issue passes. Labels, verdict
comments and the last-action rule follow State machine in `WORKFLOW.md`. The spec is locked: stories, criteria,
guardrails and design are inputs, not things to change here.

```
/spec → /ready → /architecture → build
                      │
                      ▼
                    /spec   (the code contradicts the spec)
```

## Step 1: Check entry

Any other `stage:` label: stop and name its owner. A stage that died halfway is redone from
Step 2, never skipped.

## Step 2: Read the inputs

Read the issue: User Stories, Scenarios, Acceptance Criteria, Guardrails, the design (if
`/ui-design` ran), and the **Domain** under Sizing. If Domain is missing, run
`bash ${CLAUDE_PLUGIN_ROOT}/skills/submit/scripts/detect_project_domain.sh`.

Read the repo's `CLAUDE.md` or `AGENTS.md` for its stack and protected files. The architect
follows the stack the repo uses; it never assumes one.

## Step 3: Run the architect

| Domain | Architect |
|--------|-----------|
| swift | Invoke `swift-architect` skill |
| python | Invoke `python-architect` skill |
| cpp-qt | Invoke `cpp-qt-architect` skill |
| unknown | Ask user to specify, or provide generic guidance |

Invoke the architect with the Skill tool. Writing the notes yourself is not a substitute, even
when the code looks familiar: the skill carries the domain's patterns and checks. A domain
whose architect is not installed counts as `unknown`.

**Prompt the architect with:**
```
Design architecture for issue #<N>: <title>

Stories and acceptance criteria:
<summary>

Guardrails:
<summary>

Design (if any):
<screens and accessibility IDs>

Provide:
- Component diagram (ASCII)
- Data flow
- File structure, citing existing file:line where it changes
- Key implementation decisions with their rationale
```

Check every file:line and symbol it cites against the code before keeping it.

## Step 4: Exit check (technical approach)

An implementer can start without re-deriving the architecture: the types and files to touch,
the data flow, and the decisions with their rationale are named, and every named symbol exists.

**Prove every numeric criterion is reachable** in the code as it stands, before filing: work
the number through the existing model (a quick calculation, a test run, a scratch probe) and
check that units, frames and axes agree on the way. A criterion the current model cannot reach
is a contradiction, not a build task. #942 found mid-build that its moonrise interval could
never pass, because planets spin about one axis while orbits lie in a plane at the wrong angle
to it.

**Find the existing tests this change makes false.** Search the tests that exercise the code
the notes touch (callers of the changed symbols, fixtures built on the changed values) and,
where it is cheap, run them against a scratch version of the change. List each under
`### Tests this change makes false` in the notes: the test, the check it makes now, and the
check it should make after. `/implement` plans a cycle for each, so the rewrite is approved
work, not a surprise mid-build. calsync #88 listed its #85 and #73 rewrites up front and built
them as planned; periplus #944 found #117's ring test mid-build and had no rule for it.

If the code contradicts the spec (a scenario that cannot happen, a criterion that cannot be met
without changing scope), do not design around it. Post the contradiction as an issue comment
ending in `ARCH VERDICT: #<N> route=stage:spec blocking=<what contradicts>`, then stop:

```bash
gh issue edit <N> --remove-label "stage:architecture" --add-label "stage:spec"
```

## Step 5: File it

Replace the issue's `## Technical Notes` section with the architect's output, opening with
`Filled by /architecture via <architect skill> on <date>.`, post
`ARCH VERDICT: #<N> route=stage:build blocking=none` as an issue comment, then:

```bash
gh issue edit <N> --remove-label "stage:architecture" --add-label "stage:build"
```

Report per Phase closeout in `WORKFLOW.md`.
