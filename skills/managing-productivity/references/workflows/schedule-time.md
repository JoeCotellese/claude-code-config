# Workflow 6: Schedule Time for Task

## Trigger Phrases
- "Schedule [task]"
- "Block time for [task]"
- "Put [task] on my calendar"
- "Add [task] to calendar"

## Process

1. Search Next Actions for the task by name/description

2. Extract task metadata:
   - Duration from duration field (15m → 15 minutes, 2h → 2 hours)
   - Energy level from labels
   - Context from labels

3. Check calendar for available slots:
   - Use calendar MCP to get today's and upcoming week's events
   - Find free blocks that match task duration
   - For #energy-high tasks, prioritize morning/early morning (before noon, especially before 9am)
   - For #energy-low tasks, any available time works
   - For #energy-medium tasks, prefer mid-morning or afternoon

4. Present available time slots:
   ```
   I found these available slots for "[task name]" (needs [duration]):

   Today:
   - 9:00 AM - 10:30 AM (90 min free)
   - 2:30 PM - 4:00 PM (90 min free)

   Tomorrow:
   - 8:00 AM - 10:00 AM (120 min free)

   Since this is a #energy-high task, I'd recommend tomorrow at 8:00 AM. Which slot works for you?
   ```

5. Create calendar event with user's chosen time:
   - Use calendar MCP create operation
   - Event title: Task name
   - Event notes: Include @context, #energy, duration, and Todoist task URL
   - Duration: From duration field
   - Set as busy time

6. Optionally update task in Todoist:
   - Add scheduled date/time to task description

7. Confirm: "Scheduled '[task name]' for [day] at [time]. It's on your calendar. Good luck!"

## Implementation Notes

- If task has no duration, ask user: "How long do you think this will take?"
- If no slots available today, automatically suggest tomorrow and next few days
- For recurring calendar events, avoid suggesting those time slots
- Always prioritize morning slots for #energy-high tasks
