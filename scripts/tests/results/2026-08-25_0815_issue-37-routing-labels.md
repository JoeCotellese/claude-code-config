# DoD Results — #37 dev-jawn routing-label axis

- **Date:** 2026-08-25 08:15 EDT
- **Issue:** #37 — Add routing-label axis (gate:/unattended/blocked/needs-design) to dev-jawn taxonomy
- **Branch:** feature/37-routing-labels
- **Commit:** a00984d
- **Status:** PASS
- **Domain:** config/docs (no app target). Harness = the repo's shell invariant scripts under
  `scripts/tests/`, which is the channel `/ready` assigned to every AC (`[test: check_issue_37.sh]`).

## Unit / regression suite

- `scripts/tests/check_dev_jawn.sh` → **green**, exit 0. The pre-existing #26 invariant suite
  still holds; the markdown edits to spec/ready/ui-design/WORKFLOW did not disturb its checks.

## Acceptance test

- `scripts/tests/check_issue_37.sh` → **PASS**, exit 0. 14/14 checks green. This test was
  committed at `/ready` (`c0a83a7`) before any implementation and failed 14/14 then.

## Criterion-by-criterion reconciliation

All seven ACs are `[test: scripts/tests/check_issue_37.sh]`; each maps to one or more named
checks in that script. 7/7 observed and passing.

- **AC1** — six routing labels exist (`gate:machine|human|mixed`, `unattended`, `blocked`, `needs-design`) → PASS (6 label checks).
- **AC2** — `value/L`, `effort/L`, `effort/XL` labels exist → PASS (3 label checks).
- **AC3** — `spec/SKILL.md` documents gate classification and applies a `gate:` label on create → PASS.
- **AC4** — `spec/SKILL.md` value table drops `value/XL`, keeps `effort/XL` → PASS.
- **AC5** — R8 (gate is set) present in `ready/SKILL.md` and `WORKFLOW.md` DoR → PASS.
- **AC6** — `ui-design/SKILL.md` clears `needs-design` on the final approved pass → PASS.
- **AC7** — `WORKFLOW.md` documents the routing axis, the pull query, and the `polish` note → PASS.

## Reconciliation count

Issue criteria: 7. Observed across channels: 7 (all `[test:]`). No `[ui]`, no `[manual]`. 7 = 7.

## Addendum (2026-08-25, adoption)

The version-control gap noted below was closed in-scope rather than deferred, on request:

- **AC8** — `plugins/dev-jawn/scripts/setup_labels.sh` is the taxonomy of record (all 14 labels
  with colors/descriptions, idempotent applier, `--dry-run`), and `plugins/dev-jawn/README.md`
  documents both axes, the pull query, and the one-line adoption step. → PASS.

Reconciliation is now **8/8** ACs, all `[test: scripts/tests/check_issue_37.sh]`. The manifest
was applied to this repo, which also created the previously-missing `polish` label.
