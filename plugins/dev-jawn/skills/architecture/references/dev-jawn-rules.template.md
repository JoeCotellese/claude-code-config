<!-- ABOUTME: dev-jawn rules: the only place dev-jawn's /architecture looks for repo rules. -->
<!-- ABOUTME: Lists each binding doc by level; copy to the repo root as dev-jawn-rules.md. -->

# dev-jawn rules

Each entry: `<path>[ §<sections>]: <one-line purpose>`. A doc not listed here is not a rule.

## MUST
Breaking one routes to the user for sign-off.
- STANDARDS.md §Invariants: the load-bearing invariants

## SHOULD
Deviate with a stated reason; the build continues.
- STANDARDS.md: everything not listed under MUST

## DECISIONS
Why things are the way they are. Cite them; don't re-litigate them.
- docs/DECISIONS.md

## HISTORY
Context only, never rules.
- ARCHITECTURE.md: the original milestone plan
