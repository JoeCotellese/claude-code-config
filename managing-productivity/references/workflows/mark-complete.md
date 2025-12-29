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

3. Celebrate: "Excellent! [Task] is complete."

4. **Pull Next Action from Obsidian** (if task was project-related):
   - Check if completed task had a project link in description
   - If yes, read the Obsidian project note at `/Users/joec/obsidian-vault/4_Projects/[ProjectName].md`
   - Look at the `## Next Actions` section for remaining items
   - Present the next action(s) from the backlog:
     ```
     That was part of [Project Name]. Here's what's next in your backlog:

     1. [ ] Research competitor pricing (next in queue)
     2. [ ] Draft pricing page copy
     3. [ ] Review with team

     Want to pull #1 into Todoist as your next active task?
     ```
   - If user says yes:
     - Create task in Todoist Next Actions with metadata
     - Mark it as complete (checkbox) in the Obsidian project note
   - If user says no or "later": "Got it. It'll be waiting in Obsidian when you're ready."

5. If task was NOT project-related, or no backlog exists:
   - Ask: "What's next? Want another suggestion or taking a break?"

## Implementation Notes

- Keep Todoist Next Actions to 1-2 items maximum
- The Obsidian project note is the source of truth for the full backlog
- When pulling a task, apply the same metadata inference as inbox processing
