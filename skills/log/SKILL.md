---
name: log
description: "Capture debugging and problem-solving progress to Obsidian vault. Use when user invokes /log, says 'log this', 'capture progress', or 'write that down'. Scans recent conversation for relevant context and appends timestamped notebook-style entries to a per-project dev log note."
---

# Development Log Skill

Capture the progression of debugging sessions and problem-solving discussions as concise, timestamped entries in an Obsidian vault note (one note per project).

## When to Use This Skill

- User invokes `/log`
- User says "log this", "capture progress", "write that down", "note that"
- After significant debugging progress or decisions

## Workflow

### Step 1: Detect Project Name

Derive the project name from the git remote:

```bash
git remote get-url origin 2>/dev/null | sed 's/.*[:/]\([^/]*\)\.git$/\1/' | sed 's/.*[:/]\([^/]*\)$/\1/'
```

If no git remote exists, fall back to the current directory name:

```bash
basename "$(pwd)"
```

Store the result as `PROJECT_NAME`.

### Step 2: Scan Recent Conversation

Review the last 10-15 messages for relevant problem-solving context:
- What problem/bug was being investigated?
- What approaches were tried?
- What was discovered or learned?
- What decisions were made and why?
- What code files/locations were touched?
- What are the next steps?

### Step 3: Extract Key Points

Distill into concise freeform bullet points. Think "notebook jottings" not "meeting minutes":
- Focus on progression and learnings
- Include specific file paths, function names, line numbers when relevant
- Capture the "why" behind decisions
- Note dead ends briefly (they inform future debugging)
- No rigid structure required — just bullets that capture what matters

### Step 4: Format Entry

Use this markdown format:

```markdown
## Mon D, YYYY HH:MM

### Optional session topic

- Freeform bullet points capturing what happened
- Include `file:line` references where relevant
- Note decisions, discoveries, dead ends, next steps
```

### Step 5: Write to Obsidian Vault

The dev log lives at: `~/obsidian-vault/3_Permanent Notes/Dev Log - <PROJECT_NAME>.md`

**If the file does not exist**, create it with frontmatter and header:

```markdown
---
tags:
  - type/devlog
  - project/<PROJECT_NAME>
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
---

# Dev Log — <PROJECT_NAME>

Development session notes.

---

```

**If the file already exists**:
1. Update the `updated` timestamp in the frontmatter to the current time
2. Append the new entry to the end of the file

**After writing**, confirm to the user what was logged and to which project note.

## What to Capture

- Problems/bugs being investigated
- Hypotheses formed and tested
- Key findings and breakthroughs
- Decisions made and rationale
- Code locations touched (file:line format)
- Error messages that led somewhere
- Tools/commands that helped
- Next steps identified

## What NOT to Capture

- Full conversation transcript
- Pleasantries or off-topic discussion
- Information already in previous entries
- Obvious/trivial details
- Speculation that wasn't tested

## Example Entries

### Debugging Session
```markdown
## Feb 3, 2026 14:30

### Null pointer in user creation endpoint

- API returning 500 on user creation — null pointer in `validateUser()` when email field empty
- Added null check in `src/validators/user.ts:42`
- Need test coverage for empty field edge cases
```

### Architecture Decision
```markdown
## Feb 3, 2026 16:45

### Caching strategy for recipe API

- Needed caching strategy for recipe API
- Considered Redis vs in-memory vs SQLite
- Went with in-memory LRU — 95% of requests hit same 50 recipes, Redis overkill for MVP
```

### Investigation (No Fix Yet)
```markdown
## Feb 4, 2026 09:15

### Intermittent CI test failures

- Intermittent test failures in CI, passes locally
- Increased timeouts — no change. Ran with `--runInBand` — still fails
- Failure correlates with parallel DB tests, possible connection pool exhaustion
- Next: check pool size config, add connection logging
```

## Guidelines

1. **Be concise**: Each entry should be scannable in 10 seconds
2. **Be specific**: Include file paths, line numbers, function names
3. **Be honest**: Note dead ends — they're valuable context
4. **Don't duplicate**: If something was logged before, don't repeat it
5. **Timestamp format**: Use the user's local time, format as `Mon D, YYYY HH:MM`
