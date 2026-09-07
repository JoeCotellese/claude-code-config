<!-- ABOUTME: Definition of Done results for issue #60, the R2/R7 consolidation. -->
<!-- ABOUTME: Records each acceptance criterion, the channel that observed it, and the evidence. -->

# DoD results — #60 Consolidate the reachability/repeatability counter-examples

- **Date:** 2026-09-07 16:55 EDT
- **Issue:** #60
- **Branch:** feature/60-consolidate-observation-test
- **Commit:** bf2b0e0
- **Status:** PASS
- **Domain:** unknown (config repo; `detect_project_domain.sh` returns `unknown`)

## Unit suite

`bash scripts/tests/check_dev_jawn.sh` — **green**, exit 0, output pristine.
Final line: `RESULT: PASS — dev-jawn shell invariants hold.` No unexpected errors.

## Acceptance harness

**n/a.** R7 was marked N/A at `/ready` under the `CLAUDE.md` testing exemption for config
repos and markdown work, so no acceptance test was committed and there is none to run. A
harness was deliberately not built for the five proxies: that is the `#25` over-application
failure the rubric itself records.

## Criteria

All five ACs are `[manual]` with automatable proxies. Run from
`plugins/dev-jawn/skills/ready/`. Total cost: under one second.

- **AC1 — nine counter-examples remain, each traceable to its issue.** PASS.
  Evidence: `rg -c` per key returns `#372`=1, `WPD-2606`=1, `#217 AC4b`=1, `#25`=1,
  `#142`=1, `#105`=1, `WPD-2604`=2, `#193`=1. Was 0 for `#372` before the fix; the
  structural `[test:]` example had lost its provenance and it was restored.
- **AC2 — word count in [3400, 4000].** PASS. `wc -w` = **3,999** (was 4,400). **One word** of margin.
  The ceiling bound twice during review: once restoring the `passable` leg's explanation, once
  restoring the `bc4e053` carve-out that this consolidation had destroyed. Both were content
  the band exists to protect, not bloat. The band needs an explicit re-decision before the next
  amendment to this file, or it will force the wrong trade.
- **AC3 — "untagged AC" paragraph sits with the tag bullets.** PASS.
  Evidence: line 110 minus the `[manual]` bullet at line 103 = **7**, threshold ≤ 10.
  Was 27.
- **AC4 — stated counts agree with their members.** PASS.
  Evidence in `ready/SKILL.md`: `rg -c 'seven|/7'` = **0** (was 3: frontmatter, "Audit all
  seven regardless", and `passed=5/7`). Frontmatter now reads "eight readiness criteria"; the
  verdict example reads `passed=6/8`.
  The `/code-review` sweep flagged that this proxy was scoped to one directory while the
  criterion is about agreement, so two stale counts survived outside it: `WORKFLOW.md:244`
  (`passed=7/7`) and `README.md:166` ("audits seven criteria"), both pre-existing on `main` and
  both made contradictory by this change. Fixed, and the evidence widened: repo-wide
  `rg 'seven criteria|passed=7/7|all seven'` returns **0 files**.
- **AC5 — R2 and R7 read with no two blocks repeating each other.** PASS.
  Channel: human judgment, recorded by Joe Cotellese at this run. The four principle
  passages (442 words across `:86-91`, `:112-124`, `:255-260`, `:288-294`) collapsed into
  one 261-word block; the seven remaining mentions are citations of a named leg, not
  restatements.

**Reconciliation:** 5 criteria in the issue, 5 observed, 5 passing.

## Notes

- `[manual: structural]` was resolved as a qualifier on `[manual]` rather than a fourth tag.
  `plugins/dev-jawn/skills/verify/SKILL.md` reconciles exactly three channels
  (`:42-43`, `:113`, `:119`, `:156`), so a genuine fourth tag would have broken `/verify`
  silently.
- Concurrency: another process checked out `chore/retro-submit-sweep-target` in this
  worktree mid-run, so the first commit landed there on top of an unrelated unpushed commit
  (`1b96de3`). It was cherry-picked onto this branch and that branch was restored to
  `1b96de3`, matching origin. No work was lost from either.
- `gate:machine` held in practice for AC1–AC4 but AC5 required a human, as flagged at
  `/ready`. If a future run of this shape recurs, `gate:mixed` is the honest label.
