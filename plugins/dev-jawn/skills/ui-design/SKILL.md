---
name: ui-design
effort: high
description: "UI/UX design phase between spec and implement. Invoke with `/ui-design #<issue>` or when the user says 'design the UI', 'prototype this', 'let's design #N'. Builds a static prototype (the real target template rendered with fake data — not a throwaway mock), drives it in a browser with Playwright or through the platform's own preview, pressure-tests it with a fresh-context design committee on fixed lenses sized by the effort label, iterates until only non-blocking findings remain, then amends the issue and gates to /implement. UI features only."
---

# UI/UX Design Phase

Turn a filed spec into an **approved, clickable prototype before any backend work**.

The prototype is the **real target template rendered with a fake/hardcoded context** —
not a throwaway mock. `/implement` inherits it and does zero UI rework: it just swaps
the fake context for real service calls.

This phase sits between `/spec` and `/implement`:

```
/spec  →  /ui-design  →  /implement  →  /submit
```

Run it **only for features with a UI**. Backend/CLI-only work skips this phase
(`/spec` → `/implement` directly).

## Usage

```
/ui-design #<issue_number>
```

**Also triggers on:** "design the UI for #N", "prototype #N", "let's design #N".

## Workflow Overview

```
Step 1: Fetch spec issue + create/switch the feature branch
Step 2: Build the static prototype (real template + hardcoded fake context, throwaway view/URL)
Step 3: Iteration loop (passes sized by effort/): drive UI → design committee → present → decide
Step 4: On decision — amend the issue (final UX + acceptance + screenshots), commit the template
Step 5: GATE → /implement
```

## Workflow Steps

### Step 1: Fetch Spec + Branch

```bash
gh issue view $ISSUE_NUM --json title,body,labels    # or: glab issue view $ISSUE_NUM
```

Extract the **provisional UX**, **acceptance criteria**, and **architecture** (which
template(s) and what data shape the design needs).

Create or switch to the **feature branch** — the same branch `/implement` will continue
on, so the prototype template carries forward:

```bash
EXISTING=$(git branch -a | grep -E "(feature|fix)/${ISSUE_NUM}-" | head -1 | xargs)
[ -n "$EXISTING" ] && git checkout "$EXISTING" || bash ../implement/scripts/create_feature_branch.sh $ISSUE_NUM feature <brief-desc>
```

### Step 2: Build the Static Prototype

Build the **real target template(s)** at their production path, plus a **throwaway view +
URL** that renders them with a **hardcoded fake context**. Tag the view:

```
# ponytail: prototype view — /implement replaces the fake context with real service calls.
```

- Web/Django: real template + a temporary function view + URL under a `_prototype/` prefix.
- Web/JS: the real component with a mock-data fixture.
- Non-web UI: build the real view with sample data using the platform's own preview.

**Fake data must exercise real states**, not just the happy path — include the **empty
state**, a **typical** case, and a **stress** case (e.g. the max count, long text, a failed
item). A design that only looks good with three tidy rows is not approved.

Bring the app up so the prototype is live (for this repo: `db` container + uvicorn), then
commit: `prototype: <feature>`.

### Step 3: Iteration Loop (sized by the effort label)

`/ready` recorded a committee tier in the issue from the `effort/` label. Use it rather than
re-deriving it:

- **effort/S** — one pass, one reviewer (the acceptance-criteria lens).
- **effort/M** — up to two passes, two lenses.
- **effort/L** — up to three passes, all three lenses.

Repeat up to the tier's pass count until the user decides:

1. **Drive the UI.** Capture the empty, typical, and stress states at two widths, and
   exercise the key interactions the spec calls for (drag, hover, dialog, focus).

   - **Web** — Playwright against the prototype URL; screenshot desktop **and** mobile widths.
   - **Apple platforms** — render the real view through `mcp__xcode__RenderPreview` for each
     state. On the final pass, build and drive it in the simulator with AXe, so the design is
     confirmed through the same harness that will run the Definition of Done test.

   For Playwright:

   - **Load the interaction tool schemas up front** — they're deferred, so their params
     aren't known until fetched:
     `ToolSearch("select:browser_click,browser_type,browser_select_option,browser_fill_form")`.
   - **Param convention (gotcha):** these tools take `element` (a human-readable description)
     + **`target`** (the `ref` value from the snapshot, e.g. `"e18"`) + `values`/`text` —
     **not** `ref`. Passing `ref:` fails with `expected string, received undefined at target`.
   - **Screenshot location:** pass an **absolute scratchpad path** as `filename` (or rely on
     the gitignored `.playwright-mcp/` default). `filename` is relative to cwd, so a bare
     name like `"empty.png"` lands in the repo root and shows up in `git status` — you'd then
     have to delete it before committing.

2. **Design committee — fresh contexts.** Spawn subagents (Agent tool) that did *not* build
   the prototype. Give each the issue + the screenshots (and the live URL if it can drive
   Playwright itself), and **one lens only** — overlapping lenses produce three copies of the
   same finding and no coverage of the other two. Instruct each to **pressure-test, not
   rubber-stamp**. The builder does not grade its own homework.

   The lenses, in the order the tiers add them:

   1. **Acceptance criteria coverage** across the empty, typical, and stress states. Does each
      criterion have a visible path in this design?
   2. **Accessibility** — keyboard path, focus order, contrast, tap target size, non-drag
      fallback, and how it reads under a screen reader. WCAG for web, VoiceOver and Dynamic
      Type for Apple platforms.
   3. **Platform conventions and aesthetic fit** — Apple HIG on Apple platforms, the
      platform's own idioms elsewhere, plus whether it looks like it belongs in this app.

   **Each reviewer returns a blocking finding count.** Only blocking findings force another
   pass; non-blocking findings get logged to the issue and dropped. Without that rule, a
   three-pass tier always takes three passes, because a fresh reviewer can always find one
   more thing to prefer differently.

3. **Present + decide.** Show the user the screenshots, the independent critique, and your
   recommended changes. Use **AskUserQuestion**: **Approve** / **Iterate** / **Stop**.
   - Approve → Step 4.
   - Iterate → apply changes, increment the counter, loop.
   - Stop → exit; leave the branch as-is for later.

After the tier's last pass without approval, do **not** loop again — present the best
version and ask the user to decide: approve as-is, take it over manually, or defer. The
cap is a forcing function, not a failure.

**You approve each pass. Taste is not delegated.** The committee reports blocking findings;
it does not decide whether the design is good.

### Step 4: On Decision — Finalize

- **Amend the issue:** replace the provisional UX + acceptance criteria with what was
  actually designed; attach/link the key screenshots; note the prototype template path and
  the throwaway view that `/implement` will productionize.
- Ensure the template + prototype view are **committed on the feature branch**.

### Step 5: GATE — Ready to Implement

Use **AskUserQuestion**:

```
✅ Design approved for #<issue_number>.
Prototype committed on <branch>. Ready to implement?
- Yes → /implement #<issue_number>
- Refine → more design iteration
- Stop here → implement later
```

On **Yes**, invoke the `implement` skill: `skill="implement", args="#<issue_number>"`.
`/implement` continues on this branch, wires the fake context to real services, and removes
or repurposes the throwaway prototype route.

## Success Condition

The prototype renders live in a browser (verified via Playwright screenshots across
desktop + mobile widths and the empty/typical/stress states), an independent review context
has pressure-tested it on its assigned lenses with no blocking findings left, and the user has
explicitly approved a version. Only then does the phase gate to `/implement`.

## Dependencies

- `gh` / `glab` (issue read + amend)
- Playwright MCP (drive the prototype in a browser) or `mcp__xcode__RenderPreview` on Apple platforms
- Agent tool (fresh-context design committee)
- `../implement/scripts/create_feature_branch.sh` (shared branch naming)

## Next Phase

After approval, chains to → `/implement`
