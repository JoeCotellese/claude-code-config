---
name: architecture
max_words: 1100
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

Then find the repo's architecture rules: ADRs (`docs/adr/`, `adr/`, `docs/decisions/`),
`ARCHITECTURE.md`, `STANDARDS.md`, `docs/architecture*`, `CONTRIBUTING.md`, and the pattern or
convention sections of `CLAUDE.md` or `AGENTS.md`. Read each that exists. List its path with a
one-line summary of each rule it sets, or `none found`. These repo rules outrank the domain
architect skill's defaults.

## Step 3: Run the architect

| Domain | Architect |
|--------|-----------|
| swift | Invoke `swift-architect` skill |
| python | Invoke `python-architect` skill |
| cpp-qt | Invoke `cpp-qt-architect` skill |
| unknown | Ask user to specify, or provide generic guidance |

The domain architect skills are optional: they live outside the plugin, so a config dir may
not have them. If the table's skill is not in your skill listing, pass architect skill `none`
and dispatch anyway. Do not ask the user.

Dispatch the `dev-jawn:architect` agent with the Agent tool (`subagent_type:
"dev-jawn:architect"`, never `fork`: a fork inherits the session model, and the agent pins
`model: opus`). Its brief: the issue number, the domain, the architect skill from the table,
the stack, protected files and repo rules from Step 2, and the absolute path of this `SKILL.md`. It invokes
the architect skill with the Skill tool, then runs Step 4's exit checks, and replies `ARCHITECT RESULT: notes` or
`ARCHITECT RESULT: contradiction`. Writing the notes yourself is not a substitute, even when the
code looks familiar: the agent runs Step 4's checks in a fresh context. Only an `unknown`
domain is resolved here before dispatching, since the agent cannot ask the user.

On `contradiction`, take Step 4's route to `/spec` with its evidence. On `notes`, spot-check
the cited file:line and symbols yourself, then go to Step 5.

**Prompt the architect with** (the brief is this template, no fixture design):
```
Design architecture for issue #<N>: <title>

Stories and acceptance criteria:
<summary>

Guardrails:
<summary>

Design (if any):
<screens and accessibility IDs>

Repo rules (these outrank your defaults):
<path: one-line rule, or none found>

Provide:
- Component diagram (ASCII)
- Data flow
- File structure, citing existing file:line where it changes
- Key implementation decisions with their rationale
- Repo rules followed, citing each doc by path
```

Check every file:line and symbol it cites against the code before keeping it.

## Step 4: Exit check (technical approach)

An implementer can start without re-deriving the architecture: the types and files to touch,
the data flow, and the decisions with their rationale are named, and every named symbol exists.

**Prove every numeric criterion is reachable** in the code as it stands, before filing.
Calculate it through the existing model first, then probe existing code only if the number
depends on runtime behaviour, checking that units, frames and axes agree. Otherwise list it
under `### Unproven` with the test that will check it; `/implement` builds that test first. A criterion the current model cannot reach is a contradiction, not a build task. #942 found mid-build that its moonrise interval could
never pass, because planets spin about one axis while orbits lie in a plane at the wrong angle
to it.

**Find the existing tests this change makes false.** Search the tests that exercise the code
the notes touch (callers of the changed symbols, fixtures built on the changed values). List each under
`### Tests this change makes false` in the notes: the test, the check it makes now, and the
check it should make after. `/implement` plans a cycle for each, so the rewrite is approved
work, not a surprise mid-build. calsync #88 listed its #85 and #73 rewrites up front and built
them as planned; periplus #944 found #117's ring test mid-build and had no rule for it.

**Check the design against the repo rules.** The notes list each rule doc applied under
`### Repo rules followed`, or `none found`. A design that must break a rule names the rule, its
doc path and the reason under `### Repo rule exceptions`; never break one silently.

If the code contradicts the spec (a scenario that cannot happen, a criterion that cannot be met
without changing scope), do not design around it. Post the contradiction as an issue comment
ending in `ARCH VERDICT: #<N> route=stage:spec blocking=<what contradicts>`, then stop:

```bash
gh issue edit <N> --remove-label "stage:architecture" --add-label "stage:spec"
```

## Step 5: File it

Replace the issue's `## Technical Notes` section with the lines between the first and last line
of the reply, opening with `Filled by /architecture via dev-jawn:architect (<architect skill>) on <date>.`
Re-read the issue: if that line is missing, stop with the label unchanged and report
it. Otherwise post the `ARCH VERDICT` as an issue comment under the reply's `Probes:` line:

- Notes with `### Repo rule exceptions`: the user signs off first. Post `ARCH VERDICT: #<N>
  route=stage:human blocking=repo-rule-exception` naming `stage:build` as the return state,
  then:
  `gh issue edit <N> --remove-label "stage:architecture" --add-label "stage:human"`
- Otherwise: post `ARCH VERDICT: #<N> route=stage:build blocking=none`, then:

```bash
gh issue edit <N> --remove-label "stage:architecture" --add-label "stage:build"
```

Report per Phase closeout in `WORKFLOW.md`.
