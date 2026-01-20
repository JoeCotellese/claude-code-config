# Workflow 9: Prep for Upcoming Events

## Trigger Phrases
- "What do I need to prepare for?"
- "What's coming up this week?"
- "Do I have any meetings that need prep?"
- "Check my calendar for upcoming events"
- Automatically suggested during Workflow 1 if user hasn't checked in 2+ days

## Process

1. **Fetch upcoming calendar events**:
   - Use calendar MCP for next 7 days
   - Filter for events that typically need preparation:
     - Meetings with other people (exclude personal time blocks, all-day events)
     - Events longer than 30 minutes
     - Events with specific keywords: "meeting", "call", "presentation", "demo", "interview", "review"

2. **For each event, check if preparation exists**:
   - Search Projects project for task matching event title or key people
   - Search Next Actions for tasks mentioning the event/people
   - Identify events that have NO preparation tasks

3. **Present events needing attention**:
   ```
   Here are your upcoming events that might need preparation:

   **Wednesday, Nov 13 at 2:00 PM** - AI Alliance Meeting (1 hour)
   Found project: "Prep For AI Alliance Meeting" with next action "Review meeting minutes"

   **Thursday, Nov 14 at 10:00 AM** - Client Demo with Acme Corp (1 hour)
   No prep found. Suggested actions:
   - Review demo script
   - Test demo environment
   - Prepare Q&A responses

   **Friday, Nov 15 at 3:00 PM** - 1:1 with Sarah (30 min)
   No prep found. Suggested actions:
   - Review previous 1:1 notes
   - Prepare discussion topics

   Want me to create projects/tasks for any of these?
   ```

4. **For events without preparation**:
   - Ask: "Want to create a project for '[Event Name]'?"
   - If yes:
     - Create Obsidian project note in `4_Projects/Prep for [Event Name].md`
     - Generate Obsidian URI link: `obsidian://open?vault=obsidian-vault&file=4_Projects%2FPrep%20for%20[Event Name]`
     - Create project task in Projects project named "Prep for [Event Name]" with Obsidian link in description
   - Ask: "What's the first action you need to take?" or suggest common prep tasks:
     - Review agenda/materials
     - Prepare presentation/demo
     - Research attendees
     - Gather background information
   - Add suggested action to Next Actions with metadata and reference to project

5. **Suggest scheduling prep time**:
   - For events 2+ days away: "You have 3 days before this meeting. Want to schedule prep time?"
   - For events < 2 days away: "This is coming up soon! Want to block time today for prep?"
   - Use Workflow 6 (Schedule Time for Task) if user says yes

## Implementation Notes

- Run this proactively if user hasn't done it in 2+ days (mention during Workflow 1)
- Default prep window: 7 days (configurable if user wants more/less notice)
- Ignore recurring personal events like "Check the chickens" or calendar blocks labeled "Focus time"
- For events with multiple attendees, suggest research/prep tasks
- Consider event duration: 30-min 1:1s need less prep than 1-hour client demos
- Link prep tasks back to calendar event in task notes when possible

## Common Prep Task Patterns by Event Type

- **Client meetings**: Review account history, prepare demo, update proposal
- **1:1s**: Review previous notes, prepare discussion topics, gather feedback
- **Presentations**: Build slides, practice delivery, prepare Q&A
- **Interviews**: Review candidate background, prepare questions, coordinate with team
- **Reviews**: Gather data/metrics, prepare status update, identify blockers
