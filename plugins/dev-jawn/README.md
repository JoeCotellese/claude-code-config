# dev-jawn

A phased development loop packaged as a Claude Code plugin: `/spec` → `/ready` → `/ui-design` →
`/implement` → `/verify` → `/submit`, with `/retro` as the reverse edge. The loop itself is
documented in **[skills/WORKFLOW.md](skills/WORKFLOW.md)** — read that for the Definition of
Ready, the Definition of Done, and the seven loops.

This page covers the one thing a project must set up before the loop runs: the **label
taxonomy**.

## Label taxonomy

dev-jawn drives issues with two orthogonal label axes. `/spec` sets them, `/ready` audits them
(R6 for effort, R8 for gate), and a downstream unattended loop queries them.

**Priority — how important, how big.** One `value/` and one `effort/` per issue.

- `value/S` · `value/M` · `value/L` — business impact. Value tops out at L; there is no
  `value/XL`.
- `effort/S` · `effort/M` · `effort/L` · `effort/XL` — implementation size. `effort/XL` does
  not pass the Definition of Ready; it routes back to `/spec` to be split.

**Routing — who closes it, can the loop touch it.** The axis that lets an unattended loop pick a
next item it can actually finish.

- `gate:machine` · `gate:human` · `gate:mixed` — who can close the issue. Exactly one per issue,
  required by the Definition of Ready (R8). Set at `/spec`.
- `unattended` — safe for the loop to pull with no human and no hardware. Set by `/ready`.
- `blocked` — a dependency must clear first. Set and cleared as dependencies move.
- `needs-design` — must go through `/ui-design` first. Cleared by `/ui-design` on its final
  approved pass (single owner, so it never goes stale).

**Not an axis:** `polish` is a work-type tag (cosmetic refinement), like `bug` or
`documentation`. It is outside the Definition of Ready and outside the pull query.

### The next-item pull query

A loop that wants a next item it can finish unattended queries the label side:

```
highest value/, lowest effort/, unattended AND gate:machine, NOT blocked
```

The consuming repo adds its own open/status filter on top (a Project board's `status`, or just
"issue is open"). That board lives in the consuming repo, not here — dev-jawn only exposes the
labels.

## Adopting dev-jawn in a project

The labels are the taxonomy of record in
**[scripts/setup_labels.sh](scripts/setup_labels.sh)**. Create them in a repo once:

```bash
# from the target repo, with gh authenticated
bash <path-to>/plugins/dev-jawn/scripts/setup_labels.sh

# preview the taxonomy without creating anything
bash <path-to>/plugins/dev-jawn/scripts/setup_labels.sh --dry-run
```

The script is idempotent (`--force`), so re-running it reconciles colors and descriptions after
an edit. On GitLab, translate each line in the script to `glab label create`; the names and
meanings are identical.
