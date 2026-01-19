# Workflow 8: What's My Day Look Like?

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

4. Present chronological overview with task suggestions:
   ```
   Here's your day (Tuesday, Nov 12):

   8:00 AM - 9:00 AM: FREE (1 hour)
   → Suggested: Create project reference file @computer #energy-medium (15m)

   9:00 AM - 10:00 AM: Team standup

   10:00 AM - 12:00 PM: FREE (2 hours) - Deep work time
   → Suggested: Begin documenting NG Analytics API @computer #energy-high (30m)

   12:00 PM - 1:00 PM: Lunch

   1:00 PM - 2:00 PM: FREE (1 hour)
   → Suggested: Check in on mom @phone #energy-low (15m)

   2:00 PM - 3:00 PM: Client call

   3:00 PM - 5:00 PM: FREE (2 hours)
   → Open for work

   You have 6 hours of free time today, with a prime 2-hour morning block. Want specific task suggestions for any time slot?
   ```

5. If user asks for task suggestions for specific slot:
   - Use Workflow 1 logic filtered to that time window
   - Consider time of day for energy level recommendations

## Implementation Notes

- Highlight blocks of 2+ hours as "deep work time"
- Match task suggestions to time of day (morning = high energy, afternoon = medium/low energy)
- If day is fully booked with no free blocks, say: "Your day is fully booked. No free blocks available."
- If user asks "what's tomorrow look like?", fetch next day's calendar instead
- Task suggestions should be appropriate for the time slot duration and time of day
