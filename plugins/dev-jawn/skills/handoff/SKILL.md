---
name: handoff
description: >-
  Write a HANDOFF.md briefing so a fresh Claude session can continue this work,
  then copy the resume phrase to the clipboard. Invoke with /handoff, or when the
  user says "handoff", "write a handoff", "I want to start fresh", "set up the
  next session", or the session is long and going in circles.
---

<!-- ABOUTME: Skill that writes HANDOFF.md so a fresh session can resume this one. -->
<!-- ABOUTME: Copies the resume phrase to the clipboard; the next session deletes the file. -->

# Handoff

Write `HANDOFF.md` in the project root, copy the resume phrase to the clipboard,
and tell the user it is ready. The next session reads the file, picks up the
work, and deletes the file.

claude-mem already injects the recent timeline into every new session. The
handoff adds what that timeline lacks: the goal, failed attempts and why they
failed, the current theory, and exact next steps.

## Step 1: Review the session

Review the full arc of the conversation before writing. The reader is a Claude
instance that has never seen it. Also check `git status` and the current branch
so the briefing states the real working-tree state.

## Step 2: Write HANDOFF.md

Write to `HANDOFF.md` in the current working directory. If one already exists,
overwrite it: it belongs to an earlier handoff that was never picked up.

Rules:

- Address the incoming agent, not the user.
- Be specific: file paths with line numbers, function names, commands to run.
  "Fix the auth" is useless; "`src/auth/middleware.ts:52` compares against
  `Date.now()`, should use `req.timestamp`" is useful.
- Quote error messages and failing test output verbatim.
- Every sentence carries information the agent needs. No padding.
- No tables. Use lists.

Structure:

```markdown
# Handoff

> Generated: [timestamp]
> Project: [directory], branch [branch]
> Session summary: [one sentence]

## Goal

[The end state the user wants, not the current sub-task.]

## Current State

Working:
- [confirmed working]

Broken:
- [exact symptom or error]

Uncommitted changes: [summary of git status, or "none"]

## Files in Play

- `path/to/file` : [why it matters]

## What Has Been Tried (and Why It Failed)

1. [Approach]: [root cause of failure, not "it didn't work"]

## Current Best Theory

[What you believe the right path is, and the evidence for it.]

## Next Steps

1. [Specific action with path or command]

## Key Constraints

- [User preferences stated this session, things ruled out, environment quirks]

## Memory Pointers

- Observations: [#ID : why it matters]
- Searches worth re-running: [query]
```

Omit a section only when it has nothing true to say (for example, nothing has
failed yet). For Memory Pointers, use claude-mem's search, timeline, and
get_observations tools if they are available; skip the section if not.

## Step 3: Copy the resume phrase

Run:

```bash
printf '%s' 'Read HANDOFF.md, start where we left off, then delete HANDOFF.md.' | pbcopy
```

Verify with `pbpaste`. If `pbcopy` is unavailable, print the phrase in a code
block instead.

## Step 4: Tell the user

Keep it to three lines:

1. `HANDOFF.md` is written (give its path).
2. The resume phrase is on the clipboard.
3. Run `/clear` or open a new session and paste it.

## When the next session picks up

The agent that receives the resume phrase reads `HANDOFF.md`, confirms the goal
and first next step in one or two sentences, deletes `HANDOFF.md`, then starts
on step 1. Delete the file before doing any work, so it is never committed and
never mistaken for a fresh handoff later.
