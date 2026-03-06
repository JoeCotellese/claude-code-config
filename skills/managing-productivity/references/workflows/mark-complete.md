# Workflow 5: Mark Task Complete (with Pull Next Action)

## Trigger Phrases
- "Done with [task]"
- "I completed [task]"
- "Mark [task] complete"
- "Finished [task]"

## Process

1. Search Next Actions for the task:
   ```
   mcp__todoist__find-tasks with:
     projectId: "6fHPx2qmvwhq5x4X",  # Next Actions
     searchText: "[task description]",
     limit: 5
   ```

2. Confirm which task if multiple matches, then mark complete:
   ```
   mcp__todoist__complete-tasks with:
     ids: ["task-id"]
   ```

3. Show completion confirmation (see Sample Output below)

4. **Pull Next Action from Obsidian** (if task was project-related):
   - Check if completed task had a project link in description
   - If yes, read the Obsidian project note at `/Users/joec/obsidian-vault/4_Projects/[ProjectName].md`
   - Look at the `## Next Actions` section for remaining items
   - Present the backlog and offer to pull next item

5. If task was NOT project-related, or no backlog exists:
   - Ask: "What's next? Want another suggestion or taking a break?"

## Sample Output

**Task completed (standalone):**
```
  ✓ Task completed: "Review pull request"

  Want another suggestion, or taking a break?

─────────────────────────────────────────────────────────────
  [n]ext suggestion  │  [d]one for now
```

**Task completed (project-related with backlog):**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ TASK COMPLETE                                            │
└─────────────────────────────────────────────────────────────┘

  Completed: "Get quotes from 3 contractors"
  Project:   Kitchen Renovation

── Backlog (from Obsidian) ──────────────────────────────────

  # │ Next Action                           Energy  Time
 ───┼────────────────────────────────────────────────────────
  1 │ Research countertop materials            ◐   30m    ← next
  2 │ Compare cabinet styles                   ◐    1h
  3 │ Schedule contractor visits               ○   15m

  Pull #1 into Todoist as your next active task?

─────────────────────────────────────────────────────────────
  [y]es, pull #1  │  [#] pick different  │  [l]ater
```

**After pulling next action:**
```
  ✓ Added to Next Actions: "Research countertop materials"
    └─ ◐ medium  │  30m  │  @computer

  ✓ Marked complete in Obsidian backlog

  📄 obsidian://open?vault=obsidian-vault&file=4_Projects%2FKitchen%20Renovation
```

**No backlog remaining:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ TASK COMPLETE                                            │
└─────────────────────────────────────────────────────────────┘

  Completed: "Final review with team"
  Project:   Kitchen Renovation

  🎉 No more actions in backlog — project may be complete!

  Is this project finished?

─────────────────────────────────────────────────────────────
  [y]es, complete project  │  [a]dd more actions  │  [l]ater
```

**Multiple matches found:**
```
  Found multiple tasks matching "review":

  # │ Task                                  Project
 ───┼────────────────────────────────────────────────────────
  1 │ Review pull request                   —
  2 │ Review contractor quotes              Kitchen Renovation
  3 │ Review Q1 goals                       Performance Review

  Which one did you complete?

─────────────────────────────────────────────────────────────
  [1-3] Select task  │  [c]ancel
```

## Output Components Used

- **Section Header** — `✓ TASK COMPLETE`
- **Completion confirmation** — Task name and project (if applicable)
- **Subsection header** — `── Backlog (from Obsidian) ──`
- **Task table** — Remaining backlog items with `← next` indicator
- **Celebration** — `🎉` when project backlog is empty
- **Action footer** — Pull, pick different, or later options

## Implementation Notes

- Keep Todoist Next Actions to 1-2 items maximum
- The Obsidian project note is the source of truth for the full backlog
- When pulling a task, apply the same metadata inference as inbox processing
- Update the Obsidian note to mark the pulled item as checked `[x]`
