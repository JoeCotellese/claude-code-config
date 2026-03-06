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

   Show count (see Sample Output below).

2. **Process each reminder one by one:**

   For each item, present it and apply GTD clarification.

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

5. **After processing, provide summary with items to mark complete manually.**

## Sample Output

**Starting reminders processing:**
```
┌─────────────────────────────────────────────────────────────┐
│  📱 REMINDERS PROCESSING                                    │
└─────────────────────────────────────────────────────────────┘

  Found 5 items in your Reminders Todo list.
```

**Empty inbox:**
```
┌─────────────────────────────────────────────────────────────┐
│  📱 REMINDERS PROCESSING                                    │
└─────────────────────────────────────────────────────────────┘

  ✓ Reminders inbox is at zero!
```

**Processing an item:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [1/5]

  Reminder: "Call dentist"

  Captured: Today at 2:15 PM

─────────────────────────────────────────────────────────────
  [k]eep → Todoist  │  [s]omeday  │  [n]ote  │  [d]one  │  [x] trash
```

**After moving to Todoist:**
```
  ✓ Created in Next Actions: "Call dentist to schedule cleaning"
    └─ ○ low  │  15m  │  @phone
```

**End of processing:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ REMINDERS COMPLETE                                       │
└─────────────────────────────────────────────────────────────┘

── Summary ──────────────────────────────────────────────────

  Processed:  5 items
  ✓ Todoist:   3 tasks created
  📝 Notes:    1 saved to Obsidian
  ✕ Trashed:   1

── Action Required ──────────────────────────────────────────

  Please mark these reminders complete in the Reminders app:

  ☐ Call dentist
  ☐ Research vacation spots
  ☐ Book flight
  ☐ Article idea: productivity systems
  ☐ Old note - delete
```

## Output Components Used

- **Section Header** — `📱 REMINDERS PROCESSING`
- **Progress indicator** — `[1/5]` counter
- **Item card** — Reminder name, capture time, action options
- **Confirmation messages** — `✓` for created items
- **Summary statistics** — End-of-workflow totals
- **Action Required section** — Items needing manual completion
- **Action footer** — Available commands

## Marking Reminders Complete

**Limitation:** iMCP does not currently support marking reminders as complete programmatically. After processing, remind the user to manually mark items complete in the Reminders app.

**Workaround:** Keep a list of processed reminder names and present them at the end for batch completion by the user.

## Integration with Full Inbox Processing

When user says "process inbox" or "check inboxes":

```
┌─────────────────────────────────────────────────────────────┐
│  📥 INBOX STATUS                                            │
└─────────────────────────────────────────────────────────────┘

  Todoist Inbox:     8 items
  Reminders Todo:    3 items
                    ─────────
  Total:            11 items

─────────────────────────────────────────────────────────────
  [t]odoist first  │  [r]eminders first  │  [c]ancel
```

Process the chosen inbox, then offer to process the other.

## Implementation Notes

- Reminders is a quick-capture tool - items should flow INTO Todoist, not stay in Reminders
- Process one reminder at a time to avoid overwhelming
- Apply same metadata inference rules as Todoist inbox processing
- If a reminder has a due date, consider preserving it when creating the Todoist task
