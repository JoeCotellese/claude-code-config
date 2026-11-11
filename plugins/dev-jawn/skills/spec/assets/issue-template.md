## Overview

{OVERVIEW}

---

## User Stories

{USER_STORIES}

As a <role>, I want <capability>, so that <outcome>.

---

## Scenarios

{SCENARIOS}

One short narrative per path a user actually takes, including the unhappy ones.

---

## Acceptance Criteria

{ACCEPTANCE_CRITERIA}

Each criterion is one Given/When/Then. The Then is behavior a command or test can observe, not
pixels: the design step names the elements later.

- **AC1** Given <starting state>, when <action>, then <observable result>.

## Assumptions

{ASSUMPTIONS}

Small gaps /spec answered itself because nobody was available to confirm them. Review these
with the PR; delete the section if every gap was confirmed.

---

## Guardrails

### Design constraints

{DESIGN_CONSTRAINTS}

Platform, house components or design system, and what the design must not invent (new screens,
navigation, dependencies).

### Non-goals

{NON_GOALS}

### Stop conditions

{STOP_CONDITIONS}

What makes an unattended run halt and report instead of finishing. For example: a criterion
cannot be met without changing the spec; critics still block after the last design pass.

### Rules

{RULES}

What a run must never do. For example: never weaken an assertion; never touch <protected files>.

---

## Flags

- `design-checkpoint`: {off|on} (default off). On: design stops for a human look before /ready.
- `merge`: {off|on} (default off). On: the build run merges its own PR.

---

## Technical Notes

Left empty by /spec. `/architecture` fills this after /ready passes.

---

## Analytics Events

{ANALYTICS_EVENTS}

---

## Sizing

- **Value:** {VALUE_SIZE}. {VALUE_RATIONALE}
- **Effort:** {EFFORT_SIZE}. {EFFORT_RATIONALE}
- **Domain:** {DOMAIN}

---

> Planned with `/spec` using Claude Code
