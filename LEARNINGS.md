# Learnings

Durable project knowledge. One line each, dated, symbol-prefixed.
Symbols: ⚖️ decision · 🪤 gotcha · 🧩 pattern · 🔧 tooling

- 2026-08-06 🪤 `/ready` R7 over-applies to config/docs repos; the CLAUDE.md testing exemption outranks it
- 2026-09-07 🪤 `/code-review` has no working target before a PR exists: a fresh branch has no upstream, and after `push -u` the upstream is the branch itself. Sweep the draft PR number instead
- 2026-09-07 🔧 A zero-finding code review and a review that read nothing are the same sentence in a PR body; confirm the diff was non-empty with `gh pr view --json files` before recording a pass
