# Workflow 8: What's My Day Look Like?

<!-- ABOUTME: Defines the workflow for presenting a user's daily schedule with free blocks and task suggestions. -->
<!-- ABOUTME: Uses output components for consistent, scannable terminal formatting. -->

## Trigger Phrases
- "What's my schedule today?"
- "Show me my day"
- "What's on my calendar?"
- "How does today look?"
- "What meetings do I have?"

## Process

1. Fetch today's events from calendar:
   - Use calendar MCP to get today's date range
   - Include all events (meetings, blocked time, all-day events)

2. Calculate free blocks between events

3. Fetch relevant tasks for today:
   ```
   mcp__todoist__find-tasks-by-date with:
     startDate: "today",
     limit: 20
   ```

4. Present using output components (see Sample Output below)

5. If user asks for task suggestions for specific slot:
   - Use Workflow 1 logic filtered to that time window
   - Consider time of day for energy level recommendations

## Sample Output

```
┌─────────────────────────────────────────────────────────────┐
│  📅 YOUR DAY: Tuesday, March 6                              │
└─────────────────────────────────────────────────────────────┘

  Time          Event
 ─────────────────────────────────────────────────────────────
  8:00 -  9:00  ○ FREE (1h)
                ▸ Create project reference file     ◐  15m

  9:00 - 10:00  ● Team standup

 10:00 - 12:00  ○ FREE (2h)                        ★ Deep work
                ▸ Write API documentation           ⚡  1h

 12:00 -  1:00  ░ Lunch

  1:00 -  2:00  ○ FREE (1h)
                ▸ Call mom                          ○  15m

  2:00 -  3:00  ● Client call

  3:00 -  5:00  ○ FREE (2h)

── Summary ──────────────────────────────────────────────────

  Free: 6h total  │  Meetings: 2  │  Deep work slot: 10am-12pm

─────────────────────────────────────────────────────────────
  [1-3] Start task  │  [m]ore suggestions  │  [d]one
```

## Output Components Used

- **Section Header** — `📅 YOUR DAY: {date}`
- **Schedule timeline** — Time, event/free status, suggestions
- **Energy icons** — `⚡` `◐` `○` for suggested tasks
- **Status icons** — `●` busy, `○` free, `░` buffer
- **Deep work marker** — `★` for 2+ hour morning blocks
- **Subsection header** — `── Summary ──`
- **Action footer** — Available commands

## Implementation Notes

- Highlight blocks of 2+ hours as "deep work time" with `★`
- Match task suggestions to time of day:
  - Morning (before noon) → prefer `⚡` high energy tasks
  - Afternoon → prefer `◐` medium or `○` low energy tasks
- If day is fully booked:
  ```
  ┌─────────────────────────────────────────────────────────────┐
  │  📅 YOUR DAY: Tuesday, March 6                              │
  └─────────────────────────────────────────────────────────────┘

    ⚠ Your day is fully booked. No free blocks available.

    Consider rescheduling if you need focus time.
  ```
- If user asks "what's tomorrow look like?", fetch next day's calendar
- Task suggestions should be appropriate for the time slot duration
