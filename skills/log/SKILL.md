---
name: log
description: "Capture debugging and problem-solving progress to DEVLOG.txt. Use when user invokes /log, says 'log this', 'capture progress', or 'write that down'. Scans recent conversation for relevant context and appends timestamped notebook-style entries."
---

# Development Log Skill

Capture the progression of debugging sessions and problem-solving discussions as concise, timestamped entries in a `DEVLOG.txt` file.

## When to Use This Skill

- User invokes `/log`
- User says "log this", "capture progress", "write that down", "note that"
- After significant debugging progress or decisions

## Workflow

### Step 1: Scan Recent Conversation

Review the last 10-15 messages for relevant problem-solving context:
- What problem/bug was being investigated?
- What approaches were tried?
- What was discovered or learned?
- What decisions were made and why?
- What code files/locations were touched?
- What are the next steps?

### Step 2: Extract Key Points

Distill into concise bullet points. Think "notebook jottings" not "meeting minutes":
- Focus on progression and learnings
- Include specific file paths, function names, line numbers when relevant
- Capture the "why" behind decisions
- Note dead ends briefly (they inform future debugging)

### Step 3: Format Entry

Use this markdown format:

```markdown
## Mon D, YYYY HH:MM

- **Problem**: Brief description of what was being investigated
- **Tried**: Approaches attempted
- **Found**: Key discoveries or root cause
- **Fixed/Changed**: What was done (include file:line references)
- **Next**: Outstanding items or follow-up needed
```

Not all sections are required - only include what's relevant to the session.

### Step 4: Write to DEVLOG.txt

1. Check if `DEVLOG.txt` exists in the current working directory
2. If not, create it with a header:
   ```markdown
   # Development Log

   Progress notes from debugging and development sessions.

   ---

   ```
3. Append the new entry to the file
4. Confirm to user what was logged

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

- **Problem**: API returning 500 on user creation endpoint
- **Tried**: Added logging to auth middleware - all passing
- **Found**: Null pointer in `validateUser()` when email field empty
- **Fixed**: Added null check in `src/validators/user.ts:42`
- **Next**: Add test coverage for empty field edge cases
```

### Architecture Decision
```markdown
## Feb 3, 2026 16:45

- **Context**: Needed caching strategy for recipe API
- **Options considered**: Redis vs in-memory vs SQLite
- **Decision**: In-memory with LRU eviction - simpler ops, sufficient for current scale
- **Rationale**: 95% of requests hit same 50 recipes, Redis overkill for MVP
```

### Investigation (No Fix Yet)
```markdown
## Feb 4, 2026 09:15

- **Problem**: Intermittent test failures in CI, passes locally
- **Tried**: Increased timeouts - no change
- **Tried**: Ran with `--runInBand` - still fails
- **Found**: Failure correlates with parallel DB tests, possible connection pool exhaustion
- **Next**: Check pool size config, add connection logging
```

## Guidelines

1. **Be concise**: Each entry should be scannable in 10 seconds
2. **Be specific**: Include file paths, line numbers, function names
3. **Be honest**: Note dead ends - they're valuable context
4. **Don't duplicate**: If something was logged before, don't repeat it
5. **Timestamp format**: Use the user's local time, format as `Mon D, YYYY HH:MM`
