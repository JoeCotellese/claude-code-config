---
name: autopilot
max_words: 1000
effort: high
description: "Hands-off dev-jawn run from idea or issue to an open PR, with one stop at the end. Invoke with `/autopilot #<issue>` or `/autopilot <description>`, or when the user says 'autopilot #N', 'run this hands-off', 'build it and show me at the end'. Adds the autopilot label, drives every phase in one session, builds each acceptance criterion with a fresh subagent, and stops only to ask for the merge."
---

<!-- ABOUTME: Driver for a hands-off dev-jawn run: spec through an open PR with one stop. -->
<!-- ABOUTME: Applies the Autopilot rule in WORKFLOW.md and builds each criterion in a fresh subagent. -->

# Autopilot

Read Autopilot in `${CLAUDE_PLUGIN_ROOT}/skills/WORKFLOW.md` first. That rule governs every
gate below; this skill only drives the phases in order.

**Do not end your turn between phases.** Each phase's closeout prints its Layer 1 status line
and no gate, then you invoke the next phase. Ending a turn to say "next step is X, want me to
start?" is the stall this skill exists to remove.

## Step 1: Label the issue

- `#N`: `gh issue edit <N> --add-label autopilot`. If the label does not exist, create it with
  the `autopilot` line from `${CLAUDE_PLUGIN_ROOT}/scripts/setup_labels.sh`, then retry.
- `<description>`: invoke `dev-jawn:spec` with the description and the Autopilot rule in force.
  No issue exists yet, so hold each `DECISION:` and post it when the issue is filed. Add the
  label to every issue it files, in the same step that sets `stage:`.
- **Split children:** run Steps 2 to 4 for each child in the order `/spec` filed them, one at a
  time, and give one final report covering all of them.

## Step 2: Plan and design phases

Read the issue's `stage:` label and invoke its owner, per State machine in `WORKFLOW.md`, until
the label is `stage:build`: `/spec`, `/ui-design`, `/ready`, `/architecture`. `stage:human`
means a phase stopped under the rule's stop list: report it and stop.

## Step 3: Build

Run `dev-jawn:implement` with these replacements:

- **Step 1 (clear context):** skip. Continue in this session.
- **Steps 4 and 5 (plan mode, approval):** write the same plan without plan mode, post it to
  the issue as a comment, then post
  `DECISION: #<N> gate=plan chose=posted plan why=autopilot`.
- **Step 6 (goal):** skip. This step's loop replaces it.
- **Step 7 (TDD loop):** dispatch one fresh `Agent` (`subagent_type: general-purpose`) per
  acceptance criterion, in plan order, one at a time. They share one working tree, so never in
  parallel. Each prompt carries: the issue number and branch, the criterion's full text and
  channel tag, the plan's section for it, the acceptance test path, and these rules:
  - Follow `/implement` Step 7 for this criterion only: failing test first, minimal code,
    touched tests green, one commit.
  - Never edit the acceptance test, weaken an assertion, or delete a test.
  - An existing test outside the plan that your change makes false: do not edit it. Reply with
    the test, the check it makes, and why the change makes it false.
  - A file outside the plan's file list: touch it only if the criterion cannot pass without
    it, and name it and the reason in your reply.
  - A question you would ask the user: apply the Autopilot rule in `WORKFLOW.md`, post the
    `DECISION:` comment, continue.
  - Reply with the test name, the commit SHA, and any `DECISION:` you posted, or the blocker.
- **Subagent reports outside the plan.** A test the change makes false becomes a new
  criterion: post `DECISION: #<N> gate=criterion-added chose=rewrite <test> why=<old check> is
  false after <change>; new check <check>`, then dispatch a cycle for it. A file outside the
  plan gets `DECISION: #<N> gate=scope chose=keep <file> why=<reason>`, or, if the criterion
  did not need it, revert it and file a follow-up issue.
- **Step 8 (DoD):** run `dev-jawn:dod` in this session, not in a subagent, so the
  `DOD VERDICT` line lands in this transcript. On `route=/implement`, dispatch one fix agent per
  failing criterion with the criterion list's reason, then run `/dod` again.
- **Step 9 (review gate):** skip. Go to Step 4.

**Caps.** Stop after 12 `/dod` rounds. If the same criterion fails three rounds in a row, stop:
the problem is not the implementation. A `route=/retro` or `route=/ready` stops too. Each stop
sets `stage:human`, posts why, and goes to Step 5 with what exists.

## Step 4: Submit

Run `dev-jawn:submit` Steps 1 through 7. Its committee loop fixes blocking findings itself.
Do not start Step 8's review polling: the PR now waits on the user.

## Step 5: Final report

The one stop. Report per Phase closeout in `WORKFLOW.md`, Layer 1 first:

1. Status: what a user can now do, the PR link, and anything that would surprise the user.
2. The deferred `[manual]` criteria, each with its proxy result and the evidence to look at
   (capture paths, the command to run it).
3. Every `DECISION:` the run took, one line each, from
   `gh issue view <N> --comments`, so the user can overrule any of them. List
   `gate=criterion-added` and `gate=scope` first: they changed an existing test or a file the
   plan did not name.

When any deferred criterion's evidence is captures (screenshots, renders, recordings), `open`
the key ones (one per page or view the change touches) before the stop line, so the user sees
them while deciding.

End with a typed stop, not AskUserQuestion. List each deferred `[manual]` criterion as
"AC<n>: reply pass or fail", then: "Reply `merge`, or tell me what to change." A form adds a
click and its "Stop here" branch ends the run, so merging later needs a second `/submit`.

When the user replies `merge`, run `/submit` Step 10 onward in this session. Merge only after
every deferred `[manual]` criterion has a pass. A failed one does not merge. Post it as a
`[manual]` failure on the issue, run the Step 3 loop on that criterion, and report again.
Feedback instead of `merge` is a change request: fix it under the same rule and report again.

## Success Condition

The transcript holds a `DOD VERDICT` with `status=PASS`, `PASS-with-caveats` or
`PASS-pending-manual`, a PR
URL, a final report that ends with the typed stop, and no AskUserQuestion. Any question form
means a gate skipped the Autopilot rule; note it for `/retro`.
