#!/bin/bash
# ABOUTME: Canonical dev-jawn label taxonomy and its applier for a repo.
# ABOUTME: The two axes (priority + routing) live here; run once per project to create them.

# This file IS the taxonomy of record. A project adopting dev-jawn runs it once to create the
# labels the loop depends on: /spec sets value/effort/gate, /ready reads them, and a downstream
# unattended loop queries them. Edit a description or color here, re-run, and the change lands
# (create is idempotent via --force). Pass --dry-run to print the set without touching the repo.
#
#   bash plugins/dev-jawn/scripts/setup_labels.sh            # apply to the current repo (GitHub)
#   bash plugins/dev-jawn/scripts/setup_labels.sh --dry-run  # just print the taxonomy

set -u

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# name | hex color (no #) | description
# Priority axis — how important (value) and how big (effort). /spec sets one of each.
# Value tops out at L; effort adds XL, which /ready routes back to /spec to split.
# Routing axis — who closes it (gate:*) and whether the loop may touch it. Orthogonal to priority.
LABELS=(
  "value/S|c2e0c6|Nice-to-have, minor polish"
  "value/M|0e8a16|Useful improvement, affects some users"
  "value/L|006b25|Important feature, clear user demand"
  "effort/S|fef2c0|1-2 files, clear scope, < 1 hour"
  "effort/M|fbca04|Multiple files, some investigation needed"
  "effort/L|d4a017|Cross-cutting, multi-service, needs design"
  "effort/XL|b08800|Epic-level, should be broken into sub-issues"
  "gate:machine|1d76db|Loop can close it unattended, no human/hardware"
  "gate:human|0052cc|A person or hardware must close it"
  "gate:mixed|5319e7|Both machine and human steps to close"
  "unattended|0e8a16|Safe for the loop to pull with no human/hardware"
  "blocked|b60205|Cannot proceed until a dependency clears"
  "needs-design|d876e3|Routes through /ui-design before it can be built"
  "polish|fbca04|Work-type tag: cosmetic refinement (not a gate, not priority)"
)

if [ "$DRY_RUN" -eq 0 ] && ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "❌ Not in a git repository."
    exit 1
fi
if [ "$DRY_RUN" -eq 0 ] && ! command -v gh >/dev/null 2>&1; then
    echo "❌ gh not found. Install the GitHub CLI, or create these labels by hand (see --dry-run)."
    echo "   On GitLab, translate each line below to: glab label create --name <n> --color '#<hex>' --description <d>"
    exit 1
fi

fail=0
for row in "${LABELS[@]}"; do
    IFS='|' read -r name color desc <<< "$row"
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '%-14s #%-7s %s\n' "$name" "$color" "$desc"
        continue
    fi
    if gh label create "$name" --color "$color" --description "$desc" --force >/dev/null 2>&1; then
        printf '✅ %s\n' "$name"
    else
        printf '❌ failed: %s\n' "$name"; fail=1
    fi
done

[ "$DRY_RUN" -eq 1 ] && { echo; echo "(dry run — no labels created)"; exit 0; }
if [ "$fail" -eq 0 ]; then
    echo; echo "dev-jawn labels applied. /spec, /ready, and the pull query can now use them."
else
    echo; echo "Some labels failed — check gh auth and repo permissions."
fi
exit "$fail"
