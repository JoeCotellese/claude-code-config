# Workflow 1: What Should I Be Working On?

## Trigger Phrases
- "What should I be working on?"
- "What should I do next?"
- "Suggest a task"
- "What can I work on now?"

## Process

1. **Check calendar for today's availability (automatic)**:
   - Use your primary calendar via MCP to get today's events
   - Calculate free blocks between meetings
   - Determine actual available time windows
   - Note: Prioritize morning/early morning (before noon, especially before 9am) for #energy-high tasks
   - **Proactive suggestion**: If user hasn't run Workflow 9 (Prep for Upcoming Events) recently, mention: "By the way, want me to check if you have any meetings this week that need prep?"

2. Ask the user contextual questions:
   - "Where are you right now?" → determines context (@home, @work, @computer, @errands, @phone, @anywhere)
   - "What's your current energy level?" → determines energy filter (high, medium, low)
   - (Skip asking "how much time" - we know from calendar)

3. Query Todoist Next Actions project with filters:
   ```
   mcp__todoist__find-tasks with:
     projectId: "6fHPx2qmvwhq5x4X",  # Next Actions project
     labels: ["@computer", "#energy-medium"],  # based on user context/energy
     labelsOperator: "and",
     limit: 20
   ```
   Then filter results by duration field to match available calendar windows.

4. Present the top 3-5 matching options with calendar context:
   ```
   You have 45 minutes before your 2pm meeting. Here's what makes sense right now:

   1. Review pull request @computer #energy-low (15m)
   2. Create project reference file @computer #energy-medium (15m)
   3. Look up definition @computer #energy-low (5m)

   I'd recommend #1 - it's a good fit for your available time and current energy. Want to tackle it?
   ```

5. After user completes a task:
   - Mark it complete in Todoist using `mcp__todoist__complete-tasks`
   - Ask: "Great! Want another suggestion or taking a break?"

## Implementation Notes

- Always check calendar first to determine real available time
- If user has 2+ hour free blocks in morning/early morning, prioritize #energy-high tasks
- If no results match all criteria, relax filters (remove time first, then energy, then suggest any @context items)
- Consider items without duration as "unestimated" - suggest they add metadata during processing
- If task has Obsidian project link in description, mention it for context
- If calendar check fails, fall back to asking "how much time do you have available?"
