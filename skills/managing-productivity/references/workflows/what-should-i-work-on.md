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

4. Present using output components (see Sample Output below)

5. After user completes a task:
   - Mark it complete in Todoist using `mcp__todoist__complete-tasks`
   - Show completion confirmation, offer next suggestion

## Sample Output

```
┌─────────────────────────────────────────────────────────────┐
│  📋 SUGGESTED TASKS                                         │
└─────────────────────────────────────────────────────────────┘

  You have 45 minutes before your 2pm meeting.
  Context: @computer  │  Energy: low

  # │ Task                                  Energy  Time   Context
 ───┼────────────────────────────────────────────────────────────
  1 │ Review pull request                      ○    15m   @computer
  2 │ Create project reference file            ◐    15m   @computer
  3 │ Look up definition                       ○     5m   @computer

  ╭─────────────────────────────────────────────────────────╮
  │  ▸ Recommendation: #1 — fits your time and energy       │
  ╰─────────────────────────────────────────────────────────╯

─────────────────────────────────────────────────────────────
  [1-3] Start task  │  [m]ore options  │  [s]kip
```

**After task completion:**
```
  ✓ Task completed: "Review pull request"

  Want another suggestion, or taking a break?

─────────────────────────────────────────────────────────────
  [n]ext task  │  [d]one for now
```

**When no tasks match filters:**
```
┌─────────────────────────────────────────────────────────────┐
│  📋 SUGGESTED TASKS                                         │
└─────────────────────────────────────────────────────────────┘

  ⚠ No tasks match your current filters
    Context: @errands  │  Energy: low  │  Time: 15m

  Suggestions:
  ▸ Relax energy filter (○ → ◐)
  ▸ Expand time window
  ▸ Check a different context

─────────────────────────────────────────────────────────────
  [r]elax filters  │  [a]ll tasks  │  [c]ancel
```

## Output Components Used

- **Section Header** — `📋 SUGGESTED TASKS`
- **Context line** — Shows current filters (context, energy, time)
- **Task table** — Aligned columns: #, description, energy icon, time, context
- **Recommendation callout** — Highlighted suggestion with reason
- **Action footer** — Available commands
- **Confirmation message** — For task completion
- **Warning** — When no matches found

## Implementation Notes

- Always check calendar first to determine real available time
- If user has 2+ hour free blocks in morning/early morning, prioritize #energy-high tasks
- If no results match all criteria, relax filters (remove time first, then energy, then suggest any @context items)
- Consider items without duration as "unestimated" - suggest they add metadata during processing
- If task has Obsidian project link in description, mention it for context
- If calendar check fails, fall back to asking "how much time do you have available?"
