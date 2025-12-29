# Workflow 10: Process Reminders Inbox

## Trigger Phrases
- "Process my reminders"
- "Check Reminders inbox"
- "Process Reminders Todo list"
- (Also triggered as part of "process inbox" or "check inboxes")

## Process

1. **Fetch incomplete reminders from Todo List:**
   ```
   mcp__iMCP__reminders_fetch with:
     lists: ["Todo List"],
     completed: false
   ```

   Filter results to only show items with `actionStatus: "PotentialAction"` (incomplete).

   Show count: "Found X items in your Reminders Todo list."

   If empty: "Reminders inbox is at zero!"

2. **Process each reminder one by one:**

   For each item, present it and apply GTD clarification:

   ```
   Reminder 1 of X:
   "[reminder name]"

   What would you like to do with this?
   ```

3. **Determine destination using GTD clarification:**

   a. **Is it actionable?**
      - **NO** →
        - **Reference material?** → Move to Obsidian (`2_Literature Notes/` or `3_Permanent Notes/`)
        - **Someday idea?** → Create in Todoist Someday/Maybe
        - **Trash?** → Just mark complete in Reminders

      - **YES** →
        - **< 2 minutes?** → User does it now, mark complete in Reminders
        - **Single action?** → Create in Todoist Next Actions or Waiting For, mark complete in Reminders
        - **Multi-step project?** → Create Obsidian project note + Todoist project task, mark complete in Reminders

4. **For each destination, take action:**

   **→ Todoist Task:**
   ```
   mcp__todoist__add-tasks with:
     tasks: [{
       content: "[actionable task title]",
       projectId: "[appropriate GTD project ID]",
       labels: ["@context", "#energy-level"],
       duration: "[estimated time]"
     }]
   ```
   Then mark reminder complete (user does this manually in Reminders app, or note it for batch completion).

   **→ Obsidian Note:**
   - For reference: Write to `2_Literature Notes/[Title].md` or `3_Permanent Notes/[Title].md`
   - For project: Write to `4_Projects/[ProjectName].md` with standard template

   **→ Someday/Maybe:**
   ```
   mcp__todoist__add-tasks with:
     tasks: [{
       content: "[idea/someday item]",
       projectId: "6fHPx2qjgv2CGjpP"  # Someday/Maybe
     }]
   ```

5. **After processing, provide summary:**
   ```
   Processed X reminders from Todo List:
   - Y tasks created in Todoist
   - Z notes saved to Obsidian
   - W items marked for completion

   Please mark these reminders as complete in the Reminders app:
   - [list of processed reminder names]
   ```

## Marking Reminders Complete

**Limitation:** iMCP does not currently support marking reminders as complete programmatically. After processing, remind the user to manually mark items complete in the Reminders app.

**Workaround:** Keep a list of processed reminder names and present them at the end for batch completion by the user.

## Integration with Full Inbox Processing

When user says "process inbox" or "check inboxes":

1. First check Todoist Inbox count
2. Then check Reminders Todo List count
3. Report: "You have X items in Todoist Inbox and Y items in Reminders Todo List. Which would you like to process first?"
4. Process the chosen inbox, then offer to process the other

## Implementation Notes

- Reminders is a quick-capture tool - items should flow INTO Todoist, not stay in Reminders
- Process one reminder at a time to avoid overwhelming
- Apply same metadata inference rules as Todoist inbox processing
- If a reminder has a due date, consider preserving it when creating the Todoist task
