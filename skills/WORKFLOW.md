# Feature Development Workflow

This document describes how the phase-based skills work together to guide feature development from idea to deployment.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FEATURE DEVELOPMENT LOOP                          │
│                                                                          │
│   /spec ────► /ui-design ────► /implement ────► /submit ────► Done      │
│      │         (UI only)           │               │                     │
│      ▼             ▼               ▼               ▼                     │
│    Issue       Approved         Branch            PR                     │
│    Created     Prototype        + Code            + Merged               │
│                                                                          │
│   Every arrow crosses a human gate — see the Gates table below.          │
└─────────────────────────────────────────────────────────────────────────┘
```

## The Phases

### Phase 1: `/spec` — Specification

**Purpose:** Turn an idea into a well-defined GitHub issue with requirements, UX design, and architecture.

**Invocation:**
```
/spec Add a recipe sharing feature
```

**What happens:**
1. Detects project domain (Swift, Python, C++/Qt)
2. Invokes `product-manager` skill → requirements & user stories
3. Invokes `ux-designer` skill → design guidance
4. **GATE:** "Ready for architecture?" ← waits for approval
5. Invokes domain architect skill → technical design
6. Creates GitHub/GitLab issue with all outputs (UX + acceptance marked
   **provisional — pending design** when the feature has a UI)
7. **GATE:** "Ready for the next phase?" ← waits for approval
8. If yes → invokes `/ui-design #<issue>` (UI feature) or `/implement #<issue>`
   (backend/CLI-only)

**Output:** GitHub issue with requirements, UX, and architecture

---

### Phase 2: `/ui-design` — Design (UI features only)

**Purpose:** Get an approved, clickable prototype before any backend work. The prototype is
the **real target template rendered with a fake context** — not a throwaway mock — so
`/implement` inherits it and does zero UI rework.

**Invocation:**
```
/ui-design #123
```

**What happens:**
1. Fetches the spec issue, creates/switches to the feature branch
2. Builds the real template + a throwaway view rendering it with hardcoded fake data
   covering empty, typical, and stress states
3. Iteration loop (max 3): drives the prototype with Playwright → independent review in a
   fresh context → presents screenshots + critique
4. **GATE:** "Approve / Iterate / Stop?" ← waits for approval
5. Amends the issue with the final UX + acceptance criteria, commits the template
6. **GATE:** "Ready to implement?" ← waits for approval
7. If yes → invokes `/implement #<issue>`

**Output:** Feature branch with an approved prototype template; issue UX finalized

Backend/CLI-only work skips this phase entirely.

---

### Phase 3: `/implement` — Implementation

**Purpose:** Transform the issue into tested, reviewable code with a plan-first approach.

**Invocation:**
```
/implement #123
```

**What happens:**
1. Suggests clearing context for fresh start
2. Fetches issue content (requirements, architecture)
3. Creates feature branch: `feature/123-description` (or continues the one `/ui-design`
   already started)
4. Enters **plan mode** → explores codebase, writes implementation plan. If a prototype was
   inherited, the plan wires it to real services instead of rebuilding the UI
5. **GATE:** "Plan approved?" ← waits for approval
6. Executes plan (TDD or tests-after based on project config)
7. Runs tests + code reviewer
8. **GATE:** "Ready for review?" ← waits for approval
9. If yes → invokes `/submit`

**Output:** Feature branch with committed, tested code

---

### Phase 4: `/submit` — Submission & Review

**Purpose:** Get code reviewed, iterate on feedback, merge when approved.

**Invocation:**
```
/submit
```

**What happens:**
1. Verifies on feature branch, all committed
2. Runs linter + unit tests (quick check)
3. Pushes branch to remote
4. Creates PR/MR (or finds existing one)
5. Reports PR URL, enters **review loop**
6. When feedback received → makes changes, pushes
7. **GATE:** "Review approved. Merge?" ← waits for approval
8. If yes → merges PR, cleans up branches
9. Returns to main branch

**Output:** Merged PR, clean main branch

---

## Entry Points

You don't always start at `/spec`. The workflow has multiple entry points:

| Starting Point            | Command               | Skips                     |
|---------------------------|-----------------------|---------------------------|
| Fresh idea                | `/spec <description>` | Nothing                   |
| Spec'd UI feature         | `/ui-design #123`     | Spec phase                |
| Issue already exists      | `/implement #123`     | Spec + Design             |
| Code ready for review     | `/submit`             | Spec + Design + Implement |

### Auto-Detection

When you say "work on issue #123", the system detects state:

```
Issue #123 exists?
├── No  → Start /spec
└── Yes → Branch exists?
          ├── No  → Start /implement (create branch)
          └── Yes → PR exists?
                    ├── No  → Continue /implement or /submit
                    └── Yes → Continue /submit (review loop)
```

---

## Gates (Human Checkpoints)

Every gate uses `AskUserQuestion` to pause and wait for explicit approval:

| Gate | Location                        | Question                       |
|------|---------------------------------|--------------------------------|
| 1    | `/spec` after UX                | "Ready for architecture?"      |
| 2    | `/spec` after issue             | "Ready for the next phase?"    |
| 3    | `/ui-design` each iteration     | "Approve / Iterate / Stop?"    |
| 4    | `/ui-design` after approval     | "Ready to implement?"          |
| 5    | `/implement` after plan         | "Plan approved?"               |
| 6    | `/implement` after QA           | "Ready for review?"            |
| 7    | `/submit` after review          | "Merge and deploy?"            |

Gates 3 and 4 only apply to UI features.

**Nothing proceeds automatically past a gate.** You must explicitly confirm.

---

## Skill Dependencies

Each phase skill invokes specialist skills:

```
/spec
├── product-manager      (requirements)
├── ux-designer          (design guidance)
└── swift-architect      (or python-architect, cpp-qt-architect)

/ui-design
├── Playwright MCP       (drive the prototype in a browser)
├── Agent tool           (independent review, fresh context)
└── gh/glab CLI          (read spec, amend issue with final UX)

/implement
├── EnterPlanMode        (plan before coding)
├── python-code-reviewer (or swift-swiftui-reviewer, cpp-qt-reviewer)
└── ExitPlanMode         (get plan approval)

/submit
├── Code reviewers       (pre-push check)
└── gh/glab CLI          (PR management)
```

---

## Example Full Flow

```
You: /spec Add dark mode support

Claude: [Invokes product-manager] Here are the requirements...
Claude: [Invokes ux-designer] Here's the UX guidance...
Claude: Ready for architecture? (Yes/Refine/Stop)

You: Yes

Claude: [Invokes swift-architect] Here's the architecture...
Claude: [Creates issue #47, UX marked provisional — pending design]
Claude: This feature has a UI — next is /ui-design. Ready? (Yes/Refine/Stop)

You: Yes

Claude: [Invokes /ui-design #47, creates feature/47-dark-mode]
Claude: [Builds the real view with a fake context: empty, typical, stress states]
Claude: [Playwright screenshots desktop + mobile; independent review agent critiques]
Claude: Here are the screenshots and the critique. Approve / Iterate / Stop?

You: Iterate — the toggle needs a keyboard path

Claude: [Applies changes, re-drives, re-reviews]
Claude: Approve / Iterate / Stop?

You: Approve

Claude: [Amends issue #47 with final UX + acceptance, commits the template]
Claude: Ready to implement? (Yes/Refine/Stop)

You: Yes

Claude: [Invokes /implement #47]
Claude: Recommend clearing context. Run /clear then /implement #47?

You: /clear
You: /implement #47

Claude: [Fetches issue, creates branch]
Claude: [Enters plan mode, writes implementation plan]
Claude: Plan approved? (Yes/Refine)

You: Yes

Claude: [Implements feature with TDD]
Claude: [Runs tests, code review]
Claude: Ready for code review? (Yes/No)

You: Yes

Claude: [Invokes /submit]
Claude: [Pushes, creates PR]
Claude: PR created: https://github.com/...
Claude: Awaiting review feedback...

You: Review approved, let's merge

Claude: Merge and deploy? (Yes/No)

You: Yes

Claude: [Merges PR, cleans up]
Claude: ✅ Merged! You're on main with latest changes.
```

---

## Standalone Utility

### `/git-analysis`

Not part of the phase workflow. Use anytime to analyze repository health:

```
/git-analysis
```

Provides: commit patterns, team velocity, branch hygiene, contributor stats.

---

## Quick Reference

| Command         | Purpose            | Gates                    |
|-----------------|--------------------|--------------------------|
| `/spec <idea>`  | Idea → Issue       | 2 (arch, next phase)     |
| `/ui-design #N` | Issue → Prototype  | 2 (each iteration, ship) |
| `/implement #N` | Issue → Code       | 2 (plan, review)         |
| `/submit`       | Code → Merged      | 1 (merge)                |
| `/git-analysis` | Repo health        | 0                        |

`/ui-design` runs for UI features only.
