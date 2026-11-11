---
name: ui-design
max_words: 1500
effort: high
description: "Design step of /spec, run unattended. Invoke with `/ui-design #<issue>`, through `/spec #<issue> design`, or when the user says 'design the UI', 'prototype this', 'let's design #N'. Builds a static prototype (the real target view rendered with fake data: SwiftUI `#Preview` on Apple platforms, HTML on the web), drives it with Playwright or the platform's own preview, and lets adversarial fresh-context critics attack it pass after pass until no blocking findings remain or the effort cap is hit. Writes a design log and the accessibility identifiers, then sets stage:ready. Stops for a human when the issue sets design-checkpoint or critics still block at the cap. With no UI, records 'no design needed' and sets stage:ready."
---

# UI/UX Design Step

Turn a spec's requirements into a **clickable prototype before any backend work**, without a
human in the loop. The prototype is the **real target view rendered with a fake context**, not a
throwaway mock: the build inherits it and swaps the fake context for real service calls.

Design is part of the spec. It runs after the requirements, in the same session or a later one:

```
/spec (requirements → /ui-design) → /ready → /architecture → build
```

Entry: `stage:design`, set by `/spec` for every feature. Labels, verdict comments and the
last-action rule follow State machine in `WORKFLOW.md`. The human evaluates the result at the
end, through the design log and screenshots, unless the issue sets `design-checkpoint`.

## Usage

```
/ui-design #<issue_number>
```

Normally invoked by `/spec`. **Also triggers on:** "design the UI for #N", "prototype #N".

## Workflow Overview

```
Step 1: Check entry, fetch the spec; no UI → stage:ready; else create/switch the feature branch
Step 2: Build the static prototype (real view + fake context)
Step 3: Adversarial loop (passes capped by effort/): drive UI → critics → fix → log
Step 4: Finalize: amend the issue (design, screenshots, accessibility IDs), post the design log
Step 5: Hand on: stage:human and stop, stage:spec, or stage:ready
```

## Workflow Steps

### Step 1: Fetch Spec + Branch

```bash
gh issue view $ISSUE_NUM --json title,body,labels    # or: glab issue view $ISSUE_NUM
```

Any label but `stage:design`: stop and name its owner.

**No UI to design** (no scenario or criterion involves a screen): post `DESIGN VERDICT:
#<N> route=stage:ready blocking=none` saying "no design needed", swap `stage:design` for
`stage:ready`, and stop. Do not create a branch.

Extract the **Scenarios**, the **Given/When/Then** acceptance criteria, the **Guardrails**
(design constraints and non-goals bound what you may invent: no new screens, navigation or
dependencies they do not allow), and the **Flags**.

Create or switch to the **feature branch**, so the prototype view carries forward into the build:

```bash
EXISTING=$(git branch -a | grep -E "(feature|fix)/${ISSUE_NUM}-" | head -1 | xargs)
[ -n "$EXISTING" ] && git checkout "$EXISTING" || bash ${CLAUDE_PLUGIN_ROOT}/skills/implement/scripts/create_feature_branch.sh $ISSUE_NUM feature <brief-desc>
```

### Step 2: Build the Static Prototype

Build the **real target view(s)** at their production path, fed by a **hardcoded fake
context**, rendered through **the preview idiom that stack already uses**. Never hand-roll a
stand-in in another technology: no HTML mock of a SwiftUI screen.

- **SwiftUI** — one `#Preview` per state off a hardcoded fixture. The previews *are* the harness.
- **Server-rendered web (Django, Rails)** — the real template plus a throwaway view + URL
  under a `_prototype/` prefix.
- **Component web (React, Vue, Svelte)** — the project's own story or preview harness, else a
  mock-data fixture route.
- **Anything else** — that stack's own preview, else the smallest throwaway host.

Tag whatever holds the fake data, so the build can grep for what it must productionize:

```swift
// prototype: fixture — the build swaps it for real service calls.
#Preview("Members — empty") { MemberListView(members: []) }
```

**Fake data must exercise real states:** empty, typical, and stress (max count, long text, a
failed item). Confirm it renders, then commit: `prototype: <feature>`.

### Step 3: Adversarial Loop (capped by the effort label)

The cap comes from the issue's `effort/` label:

- **effort/S and effort/M** — up to 2 passes.
- **effort/L** — up to 4 passes.
- **effort/XL** — never reaches this step; `/spec` splits it.

Each pass:

1. **Drive the UI.** Capture empty, typical, and stress states at two widths, and exercise the
   interactions the scenarios call for (drag, hover, dialog, focus).
   - **Web** — Playwright against the prototype URL; desktop **and** mobile widths.
   - **Apple platforms** — `mcp__xcode__RenderPreview` for each state. On the final pass, build
     and drive it in the simulator with AXe, the same harness the Definition of Done uses.

   For Playwright:
   - **Load the interaction schemas up front** (they are deferred):
     `ToolSearch("select:browser_click,browser_type,browser_select_option,browser_fill_form")`.
   - **Param gotcha:** these take `element` (description) + **`target`** (the snapshot `ref`,
     e.g. `"e18"`), **not** `ref`. Passing `ref:` fails with `expected string, received undefined at target`.
   - **Screenshots:** pass an **absolute scratchpad path** as `filename`. A bare name lands in
     the repo root and shows up in `git status`.

2. **Adversarial critics, fresh contexts.** Spawn subagents (Agent tool) that did *not* build
   the prototype, one per lens, all four every pass. Give each the issue and the screenshots
   (and the live URL if it can drive Playwright). Each one's job is to **break the design**,
   not to review it: find the input, state, or user it fails for. The builder does not grade
   its own homework.

   1. **Spec fit** — a Given/When/Then this design cannot satisfy, a scenario with no path, or a
      screen, control or flow no story asks for or the guardrails forbid.
   2. **States** — empty, error, loading, very long text, the largest Dynamic Type or zoom.
   3. **Accessibility** — keyboard path, focus order, contrast, tap target size, non-drag
      fallback, screen reader reading order. WCAG on web, VoiceOver on Apple platforms.
   4. **Platform fit** — Apple HIG or the platform's idioms, house components over custom
      widgets, and whether it looks like it belongs in this app.

   **Each critic returns a blocking finding count** with each blocking finding stated. Only
   blocking findings force another pass; log non-blocking ones and drop them. Without that rule
   every pass finds one more preference and the loop always runs to the cap.

3. **Fix and log.** Apply a fix for every blocking finding yourself, choosing within the
   guardrails. Append the pass to the **design log**: what each critic blocked, what you
   changed, what you chose between and why.

Exit when a pass returns zero blocking findings, or at the cap. At the cap, keep the version
with the fewest blocking findings and record the unresolved ones in the design log as open.
This is best effort: do not stop to ask, and do not loop past the cap. Blocking findings still
open at the cap go to the user in Step 5.

### Step 4: Finalize

- **Amend the issue:** add a **Design** section with the view's path, the key screenshots,
  and what the build must productionize (the fixture, or the throwaway route).
- **Name the accessibility identifier for every element a Given/When/Then touches.** Reuse
  identifiers the project already ships before inventing new ones, in the project's naming
  style:

  ```bash
  rg -o 'accessibilityIdentifier\("([^"]+)"\)' -r '$1' --no-filename --glob '*.swift' | sort -u
  ```

- **Post the design log** as an issue comment titled `Design log`: each pass, the critics'
  blocking findings, the changes, the open findings at exit.
- Commit the view, with its fixtures or prototype route, on the feature branch.

### Step 5: Hand On

Post the verdict comment, then swap `stage:design` for the label it routes to:

- **A criterion the design cannot meet** without changing the spec:
  `DESIGN VERDICT: #<N> route=stage:spec blocking=<criterion>`.
- **`design-checkpoint` set, or blocking findings open at the cap:**
  `DESIGN VERDICT: #<N> route=stage:human blocking=<checkpoint, or the findings>`, naming
  `stage:ready` as the return state. Call `PushNotification`, report per Phase closeout
  (WORKFLOW.md), and stop. `/spec #<N>` resumes it with the user's call: approve
  (`stage:ready`), iterate (`stage:design`), change the spec (`stage:spec`), or Tell me more
  (Layer 2).
- **Otherwise:** `DESIGN VERDICT: #<N> route=stage:ready blocking=none`. Do not stop; `/spec`
  runs the next owner.

## Success Condition

The prototype renders across empty, typical and stress states (Playwright screenshots at two
widths on web; every `#Preview` plus a final simulator run on Apple platforms), four
adversarial critics have attacked every pass, the loop exited on zero blocking findings or at
the cap with the open findings logged, and the issue carries the Design section, the
accessibility identifiers and the design log.

## Dependencies

- `gh` / `glab` (issue read, amend, labels)
- Playwright MCP, or `mcp__xcode__RenderPreview` and AXe on Apple platforms
- Agent tool (fresh-context critics)
- `${CLAUDE_PLUGIN_ROOT}/skills/implement/scripts/create_feature_branch.sh`

## Next Phase

Back to → `/spec`, which hands off to `/ready`.
