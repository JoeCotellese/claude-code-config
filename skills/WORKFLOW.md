# Feature Development Loop

How the phase skills work together to drive an issue from idea to merged code.

This is a **loop**, not a pipeline: phases can route work backwards, and two phase interiors
run unattended under `/goal` until a printed condition holds.

## Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        FEATURE DEVELOPMENT LOOP                              │
│                                                                              │
│   /spec ──► /ready ──► /ui-design ──► /implement ──► /submit ──► merged      │
│               │  ▲       (UI only)        │  ▲          │                    │
│               │  │           │  ▲         │  │          │                    │
│               ▼  │           ▼  │         ▼  │          ▼                    │
│            back to        design      /verify        review                  │
│            /spec on       committee   fails ──┘      committee               │
│            DoR fail       blocks ─────┘                                      │
│                                                                              │
│   ═══ unattended under /goal ═══     ─── human gate ───                      │
│   /ready, /implement                 /spec, /ui-design, /submit              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## The primitives and what each is for

Four different mechanisms, no overlap. Picking the wrong one is the most common mistake.

- **Skills** carry the standards. `/ready` holds the Definition of Ready rubric, `/verify`
  holds the Definition of Done procedure. They document what good looks like. They do not
  contain iteration counters.
- **`/goal`** drives phase interiors. It re-runs a turn until a condition holds, so a phase
  that needs "keep fixing until tests are green" uses a goal rather than hand-written loop
  logic. One goal per session, so goals are set per phase, never per feature.
- **Fresh-context `Agent` calls** are the review committees. The builder never grades its own
  work.
- **`/loop`** polls external state that changes without you: CI status and MR comments after
  `/submit`. Nothing else.

### The constraint that shapes every exit condition

The `/goal` evaluator **does not call tools**. It only judges what has been printed into the
conversation. Therefore every phase exit condition must be provable by a printed artifact:

- Good: a `DOR VERDICT:` line, a test summary with a failure count, an AXe result file path
  with `status: PASS`.
- Useless: "the design is good", "the code is clean", "acceptance criteria are met" with
  nothing printed that shows how.

This is why the Definition of Done is an AXe run. It produces a PASS/FAIL the evaluator can
read. Prose cannot close a loop.

## Definition of Ready

An issue is ready to implement when all of these hold. `/ready` audits them and prints a
pass/fail line per criterion.

- **R1 User stories** — at least one, in role/action/benefit form, each with acceptance
  criteria.
- **R2 Observable acceptance criteria** — every AC names a UI element or an app state a test
  can assert. "Feels responsive" fails. "Tapping `saveRecipeButton` shows `recipeSavedToast`
  within 2s" passes.
- **R3 Identifier contract** — every element an AC references has a named
  `accessibilityIdentifier`. Without this the DoD test cannot be written.
- **R4 Design artifact** — user-facing work has approved screens meeting Apple HIG and the
  app's existing aesthetic. Missing design routes to `/ui-design`, not to `/spec`.
- **R5 Technical approach** — the types and files to touch, the data flow, and the decisions
  already made. An implementer can start without re-deriving the architecture.
- **R6 Bounded scope** — an `effort/` label is present and is not XL. XL routes back to
  `/spec` to be split.
- **R7 DoD test exists** — an AXe YAML under `scripts/uitests/` whose `success_criteria` map
  one-to-one onto the acceptance criteria. Non-UI work names the unit or integration tests
  instead.

R7 is the load-bearing one. **The acceptance test is authored before any code**, which is
what makes the Definition of Done objective rather than aspirational.

## Definition of Done

The AXe test written at `/ready` passes against the built app, and the unit suite is green.

`/verify` runs it and writes `scripts/uitests/results/YYYY-MM-DD_HHMM_<name>.md` with a
status of PASS, FAIL, or PASS (with caveats). A FAIL routes back to `/implement`.

## The phases

### `/spec <description>` — human gated

Unchanged in shape: product-manager, then ux-designer, then a gate, then the architect,
sizing, and issue creation. Two additions:

- Acceptance criteria must be written in the observable form R2 requires.
- The UX section names the `accessibilityIdentifier` for every element an AC references.

Ends by printing the `/goal` command for `/ready`.

### `/ready #N` — unattended under `/goal`

Audits the issue against the Definition of Ready, **repairs what it can**, and routes what it
cannot. It rewrites vague ACs into observable form, names missing identifiers, derives the
AXe DoD test, creates the feature branch, and commits the test.

Prints a fixed verdict line the goal evaluator reads:

```
DOR VERDICT: #347  status=PASS  passed=7/7  blocking=none  route=/ui-design
```

Routes: `/spec` when the problem is scope or missing requirements, `/ui-design` when only the
design is missing, `/implement` when ready and no UI work is needed.

### `/ui-design #N` — human gated

Three design passes. Each pass renders the **real SwiftUI view** through
`mcp__xcode__RenderPreview` for the empty, typical, and stress states, then a committee of
fresh-context agents reviews the renders on fixed non-overlapping lenses:

- Apple HIG conformance and fit with the app's existing aesthetic
- Accessibility: VoiceOver order, Dynamic Type, contrast, tap target size
- Acceptance criteria coverage across all three states

Each reviewer returns a **blocking finding count**. Only blocking findings force another
pass; non-blocking findings are logged to the issue and dropped. Without that rule three
passes always runs three passes.

The final pass builds and drives the view in the simulator with AXe, so the design is
confirmed interactively using the same harness that will run the DoD test.

You approve each pass. Taste is not delegated.

### `/implement #N` — unattended under `/goal`

Plan mode and plan approval are still a human gate. After the plan is approved, the
implementation runs under a goal whose condition is the Definition of Done: unit tests green
and the AXe test PASSing. `/verify` runs inside that loop.

### `/submit` — human gated

Adds a code review committee before the MR is opened, on fixed lenses:

- Correctness against the acceptance criteria
- Swift concurrency and main-actor safety
- Test adequacy: would each test still fail if the fix were reverted

Blocking findings stop the submission. After the MR exists, `/loop` handles polling for CI
and review comments.

### `/retro` — after any failure

When DoR fails, a committee blocks, or the DoD test fails, record the cause and amend the
upstream template that let it through. Without this the loop is a longer straight line.

## Size gating

Committee cost scales with the `effort/` label. `/ready` records the gate in the issue so
later phases do not re-derive it.

- **effort/S** — one design pass, one reviewer, one code reviewer.
- **effort/M** — up to two design passes, two lenses, two code lenses.
- **effort/L** — full three passes, three lenses, three code lenses.
- **effort/XL** — does not pass DoR. Split it first.

## Gates

Nothing crosses these without you.

- `/spec` after UX: ready for architecture?
- `/spec` after issue: ready for the next phase?
- `/ui-design` each pass: approve, iterate, or stop?
- `/implement` after plan: plan approved?
- `/submit` after review: merge?

`/ready` has no gate. It either passes, repairs, or routes, and every outcome is printed.

## Entry points

- Fresh idea: `/spec <description>`
- Existing issue of unknown quality: `/ready #N`
- Ready issue with a UI: `/ui-design #N`
- Ready issue, no UI: `/implement #N`
- Code already written: `/submit`

Start at `/ready` when you did not write the issue yourself or it has been sitting a while.

## Standalone utilities

- `/git-analysis` — repository health, not part of the loop.
- `/verify #N` — run the DoD test on demand, outside `/implement`.
