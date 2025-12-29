# Workflow 7: Find Deep Work Time

## Trigger Phrases
- "When can I do deep work?"
- "Find time for focused work"
- "Show me blocks for high-energy tasks"
- "When should I work on [high-energy task]?"

## Process

1. Check calendar for this week:
   - Use calendar MCP to fetch 7-day range from today
   - Find free blocks of 2+ hours (ideal for deep work)
   - Prioritize morning/early morning slots (before noon, especially before 9am)

2. Search Next Actions for #energy-high tasks:
   ```
   mcp__todoist__find-tasks with:
     projectId: "6fHPx2qmvwhq5x4X",  # Next Actions
     labels: ["#energy-high"],
     limit: 20
   ```
   Sort by duration (longest first, as they benefit most from deep work blocks)

3. Present available deep work slots with task suggestions:
   ```
   Here are your best deep work blocks this week:

   **Tuesday, Nov 14**
   - 8:00 AM - 11:00 AM (3 hours free) - Prime time
     Suggested: Update EyeGuide video API (2h) @computer #energy-high

   **Thursday, Nov 16**
   - 9:00 AM - 12:00 PM (3 hours free) - Prime time
     Suggested: Look at Shopify APIs (1h) @computer #energy-high

   **Friday, Nov 17**
   - 2:00 PM - 5:00 PM (3 hours free)
     Available for deep work

   Want me to schedule any of these tasks?
   ```

4. If user says yes:
   - Enter Workflow 6 (Schedule Time for Task) for the chosen task

## Implementation Notes

- Define "deep work blocks" as 2+ hours of continuous free time
- Morning blocks (before noon) are "prime time" and should be highlighted
- If no 2+ hour blocks available, suggest the longest available blocks with a note: "No full deep work blocks available, but here are your longest stretches"
- Consider back-to-back 1-hour blocks as viable for deep work if there's no meeting between them
