# Calendar Integration Reference

This document provides detailed guidance on integrating Apple Calendar (via iMCP) with the GTD productivity system.

## Core Principles

### Calendar as Reality Check
The calendar represents **actual available time**, not estimated availability. Always check the calendar before suggesting tasks to ensure recommendations fit real-world constraints.

### Time of Day Energy Mapping
- **Early morning (6am-9am)**: Prime time for #energy-high tasks (best focus, fewest interruptions)
- **Morning (9am-12pm)**: Good for #energy-high and #energy-medium tasks
- **Afternoon (12pm-5pm)**: Better for #energy-medium and #energy-low tasks
- **Evening (5pm+)**: Primarily #energy-low tasks unless specifically energized

### Deep Work Blocks
- **Minimum**: 2 hours of continuous free time
- **Optimal**: 3+ hours, preferably in morning
- **Prime slots**: Before noon, especially before 9am
- **Acceptable**: Any 2+ hour block if morning unavailable

## Getting Current Time

Before making any time-based comparisons (determining if events are "upcoming", "in progress", or "past"), you **must** first obtain the current time.

**Tool**: `date` (bash)

```bash
date "+%A, %B %d, %Y at %I:%M %p"
```

**Returns**: Day of week, full date, and current local time (e.g., `"Friday, March 07, 2026 at 02:15 PM"`)

**Why this matters**: Without checking the current time first, you cannot accurately determine:
- Whether a meeting is "coming up" vs "already over"
- Which free block the user is currently in
- Whether to show "← You are here" annotations

**Always call this before**:
- Workflow 1: "What Should I Be Working On?"
- Workflow 8: "What's My Day Look Like?"
- Any time you need to compare against calendar events

## Using iMCP Calendar Tools

### 1. Fetching Calendar Events (Summary)

**Tool**: `mcp__iMCP__events_fetch`

Returns **summary fields only** for efficient listing. Use `events_get` when you need full details.

**Summary fields returned:**
- `identifier`, `title`, `start`, `end`, `calendar`
- `availability`, `isAllDay`, `isOrganizer`, `location`
- `attendeeCount` (number only, not attendee details)
- `hasNotes`, `hasUrl` (booleans—not actual content)

**Basic usage for today's availability**:
```
mcp__iMCP__events_fetch({
  calendars: ["Personal"],
  start: "2025-11-12T00:00:00Z",  // Today at midnight (UTC)
  end: "2025-11-12T23:59:59Z"      // Today at end of day (UTC)
})
```

**Getting this week's events for deep work planning**:
```
mcp__iMCP__events_fetch({
  calendars: ["Personal"],
  start: "2025-11-12T00:00:00Z",   // Today (UTC)
  end: "2025-11-19T23:59:59Z"       // 7 days from now (UTC)
})
```

**Parameters**:
- `calendars`: Array of calendar names, use `["Personal"]` as default
- `start`: ISO 8601 datetime for range start
- `end`: ISO 8601 datetime for range end
- `includeAllDay`: Set to `true` to include all-day events (default: true)

### 1b. Getting Full Event Details

**Tool**: `mcp__iMCP__events_get`

Use this when you need the actual notes content, creation/modification timestamps, or other details not returned by `events_fetch`.

**Additional fields returned:**
- `notes` (full content, not just hasNotes boolean)
- `createdAt`, `modifiedAt` (timestamps)
- `hasRecurrenceRules` (boolean)

**Usage**:
```
mcp__iMCP__events_get({
  identifier: "event-identifier-from-fetch"
})
```

**When to use each:**
| Need | Tool |
|------|------|
| List events for a date range | `events_fetch` |
| Check availability/free time | `events_fetch` |
| Read meeting notes or description | `events_get` |
| Check if event was recently modified | `events_get` |

### 2. Creating Calendar Events (Time Blocking)

**Tool**: `mcp__iMCP__events_create`

**Example**: Block time for a task
```
mcp__iMCP__events_create({
  calendar: "Personal",
  title: "Update EyeGuide video API",
  start: "2025-11-13T13:00:00Z",    // Tomorrow at 8am EST (UTC)
  end: "2025-11-13T15:00:00Z",      // Tomorrow at 10am EST (2 hours, UTC)
  notes: "@computer #energy-high #time-2h\n\nobsidian://open?vault=obsidian-vault&file=4_Projects/EyeGuide",
  availability: "busy"
})
```

**Event structure**:
- `calendar`: "Personal" (as configured)
- `title`: Task name from next-actions.md
- `start`/`end`: ISO 8601 datetime
- `notes`: Include @context, #energy, #time tags, and Obsidian link if applicable
- `availability`: Always "busy" for time blocking

**Date Format Requirement:**
All dates MUST include timezone indicator (`Z` for UTC). Without it, you'll get:
`Error: Invalid start or end date format. Expected ISO 8601 format.`

### 3. Updating Calendar Events

**Tool**: `mcp__iMCP__events_update`

Modify existing events. Get the `identifier` from `events_fetch` first.

**Example**: Reschedule an event
```
mcp__iMCP__events_update({
  identifier: "event-identifier",
  start: "2025-11-14T14:00:00Z",
  end: "2025-11-14T15:00:00Z"
})
```

**Example**: Update event details
```
mcp__iMCP__events_update({
  identifier: "event-identifier",
  title: "Updated Meeting Title",
  notes: "New notes content",
  location: "https://meet.google.com/xyz"
})
```

**Parameters**:
- `identifier`: (required) Event identifier from `events_fetch`
- `span`: For recurring events: `"thisEvent"` (default) or `"futureEvents"`
- `title`, `start`, `end`, `notes`, `location`, `availability`: Fields to update

### 4. Deleting Calendar Events

**Tool**: `mcp__iMCP__events_delete`

Delete or cancel events. For recurring events, can delete just one occurrence or all future occurrences.

**Example**: Delete single event or occurrence
```
mcp__iMCP__events_delete({
  identifier: "event-identifier",
  span: "thisEvent"
})
```

**Example**: Delete all future occurrences of recurring event
```
mcp__iMCP__events_delete({
  identifier: "event-identifier",
  span: "futureEvents"
})
```

**Parameters**:
- `identifier`: (required) Event identifier from `events_fetch`
- `span`: `"thisEvent"` (default) or `"futureEvents"` for recurring events

**Note**: If you're the organizer with attendees, deleting sends cancellation notices.

### 5. Listing Available Calendars

**Tool**: `mcp__iMCP__calendars_list`

Use this on first run to verify "Personal" calendar exists:
```
mcp__iMCP__calendars_list()
```

If "Personal" not found, ask user which calendar to use as default.

## Calculating Free Time Blocks

### Algorithm for Finding Free Blocks

Given a list of calendar events for a day:

1. **Sort events by start time**
2. **Identify gaps between events**:
   - First block: Start of day (8am default) to first event start
   - Between events: Previous event end to next event start
   - Last block: Last event end to end of day (6pm default)
3. **Filter by minimum duration**:
   - For task suggestions: Match task #time tag
   - For deep work: Minimum 2 hours
4. **Calculate duration**: `(end_time - start_time) in minutes`

### Example Calculation

**Calendar events**:
- 9:00 AM - 10:00 AM: Team standup
- 2:00 PM - 3:00 PM: Client call

**Free blocks**:
1. 8:00 AM - 9:00 AM (60 minutes)
2. 10:00 AM - 2:00 PM (240 minutes) ⭐ Deep work block
3. 3:00 PM - 6:00 PM (180 minutes) ⭐ Deep work block

**Task fitting**:
- #time-5m tasks: Fit in all blocks
- #time-15m tasks: Fit in all blocks
- #time-30m tasks: Fit in all blocks
- #time-1h tasks: Fit in all blocks
- #time-2h tasks: Fit in blocks 2 and 3 only

## Matching Tasks to Calendar Availability

### Step-by-Step Matching Process

1. **Fetch calendar events** for relevant time period
2. **Calculate free blocks** (see algorithm above)
3. **Read tasks** from `5_GTD/next-actions.md`
4. **Filter tasks** by:
   - Context (@computer, @phone, etc.) - user-specified
   - Energy level (#energy-high/medium/low) - user-specified
   - Time duration - **must fit in available blocks**
5. **Prioritize recommendations**:
   - For morning blocks: Suggest #energy-high tasks first
   - For afternoon blocks: Suggest #energy-medium or #energy-low tasks
   - For short blocks (< 30 min): Suggest quick wins (#time-5m, #time-15m)
   - For long blocks (2+ hours): Suggest deep work (#time-1h, #time-2h)

### Example: "What Should I Be Working On?" with Calendar

**Scenario**:
- Current time: 10:15 AM
- Next meeting: 2:00 PM (in 3 hours 45 minutes)
- User context: @computer
- User energy: medium

**Available time**: 225 minutes (3h 45m)

**Task filtering**:
```
From next-actions.md @computer section:
1. "Update EyeGuide video API" @computer #energy-high #time-2h ✓ Fits
2. "Look at Shopify APIs" @computer #energy-high #time-1h ✓ Fits
3. "Begin documenting NG Analytics" @computer #energy-high #time-30m ✓ Fits
4. "Create project reference" @computer #energy-medium #time-15m ✓ Fits
5. "Look up definition" @computer #energy-low #time-5m ✓ Fits
```

**Recommendation logic**:
- It's still morning (10:15 AM) - good time for #energy-high tasks
- User specified #energy-medium - respect user's self-assessment
- Suggest #energy-medium tasks first, then easier #energy-low tasks
- Could tackle one #time-2h task with buffer, or multiple smaller tasks

**Output**:
```
You have 3 hours and 45 minutes before your 2pm meeting. Here's what makes sense:

1. Create project reference @computer #energy-medium #time-15m
2. Look up definition @computer #energy-low #time-5m

Since you have a long block, you could also tackle:
3. Begin documenting NG Analytics @computer #energy-high #time-30m

I'd recommend starting with #1 - it matches your energy level. What do you want to tackle?
```

## Time Blocking Strategies

### When to Suggest Time Blocking

Automatically suggest time blocking for:
1. **#energy-high tasks** - Protect focus time
2. **#time-2h tasks** - Need dedicated blocks
3. **Tasks mentioned multiple times** - Clear priority signal
4. **Tasks with project deadlines** - If project has due date metadata

### Finding Optimal Time Slots

**Priority order for #energy-high tasks**:
1. Early morning slots (6am-9am) - if user is early riser
2. Morning slots (9am-12pm)
3. Longest available blocks (even if afternoon)

**Priority order for #energy-medium tasks**:
1. Mid-morning (9am-11am)
2. Early afternoon (1pm-3pm)
3. Any available slot

**Priority order for #energy-low tasks**:
1. Any available slot
2. Between meetings (fill gaps)
3. End of day

### Creating Effective Calendar Events

**Event title**: Use task name exactly as in next-actions.md

**Event notes format**:
```
@computer #energy-high #time-2h

obsidian://open?vault=obsidian-vault&file=4_Projects/EyeGuide
```

**Duration**: Use #time tag to set end time:
- #time-5m → 5 minutes
- #time-15m → 15 minutes
- #time-30m → 30 minutes
- #time-1h → 60 minutes
- #time-2h → 120 minutes

**Obsidian link format**:
- If task references a project: `obsidian://open?vault=obsidian-vault&file=4_Projects/ProjectName`
- Link is clickable from calendar app

## Deep Work Scheduling

### Identifying Deep Work Opportunities

**Criteria for deep work block**:
- Minimum 2 hours continuous free time
- No meetings before or after (buffer for flow state)
- Preferably morning (best cognitive performance)

**Search pattern**:
1. Get week's calendar events
2. Find all 2+ hour gaps
3. Rank by:
   - Time of day (morning > afternoon > evening)
   - Duration (longer > shorter)
   - Day of week (earlier in week > later, for momentum)

### Matching Deep Work to Tasks

1. Read all #energy-high tasks from next-actions.md
2. Sort by #time tag (longest first)
3. Match longest tasks to longest/best time blocks
4. Present pairings to user with rationale

**Example output**:
```
Your best deep work blocks this week:

**Wednesday, 8:00 AM - 11:00 AM** (3 hours) ⭐ Prime time
  Suggested: Update EyeGuide video API #time-2h
  Why: Morning slot, perfect duration match, high-energy task

**Friday, 2:00 PM - 5:00 PM** (3 hours)
  Suggested: Look at Shopify APIs #time-1h
  Why: Long block available, could tackle multiple tasks

Want me to schedule either of these?
```

## Daily Schedule Overview

### Format for "What's My Day Look Like?"

**Prerequisites**:
1. Run `date "+%A, %B %d, %Y at %I:%M %p"` to get the current time
2. Parse the time to compare against event start/end times

**Structure**:
1. Get current time from `date`
2. Show all events chronologically
3. Calculate free blocks between events
4. Mark current time position ("← You are here") by comparing current time against event times
5. Suggest appropriate tasks for each free block
6. Highlight deep work opportunities
7. Summarize total free time

**Time block annotations**:
- ⭐ for 2+ hour blocks (deep work potential)
- → for task suggestions
- **Bold** for current/next block
- "← You are here" for blocks containing the current time (determined by comparing `date` output to block start/end)

**Example** (assuming `date` returned `"Tuesday, November 12, 2025 at 08:15 AM"`):
```
Here's your day (Tuesday, Nov 12):

**8:00 AM - 9:00 AM: FREE (1 hour)** ← You are here (it's 8:15 AM)
→ Suggested: Create project reference @computer #energy-medium #time-15m

9:00 AM - 10:00 AM: Team standup

10:00 AM - 2:00 PM: FREE (4 hours) ⭐ Deep work time
→ Suggested: Update EyeGuide video API @computer #energy-high #time-2h

2:00 PM - 3:00 PM: Client call

3:00 PM - 6:00 PM: FREE (3 hours) ⭐ Deep work time
→ Open for work

Total free time: 8 hours with 2 prime deep work blocks
```

## Edge Cases and Error Handling

### No Calendar Events Found
- **Likely cause**: Fully free day
- **Response**: "Your calendar is clear today. You have the full day for deep work!"
- **Action**: Suggest longest/highest-priority tasks

### Calendar API Error
- **Fallback**: Ask user "How much time do you have available?"
- **Continue**: Use traditional workflow without calendar integration
- **Log**: Note that calendar integration failed (don't break the workflow)

### Task Has No #time Tag
- **For suggestions**: Skip or ask user to estimate
- **For time blocking**: Ask "How long do you think this will take?" before scheduling

### All Day Fully Booked
- **Response**: "Your day is fully booked. No free blocks available."
- **Suggestion**: "Want to see tomorrow's availability or reschedule something?"

### Multiple Calendar Matches
- **Resolution**: Use "Personal" calendar by default (configured in preferences)
- **Alternative**: If "Personal" doesn't exist, list calendars and ask user to choose

## Proactive Event Preparation (Workflow 9)

### Scanning for Upcoming Events

**Goal**: Identify meetings/events in next 7 days that might need preparation.

**Algorithm**:
1. Fetch events 7 days forward: `mcp__iMCP__events_fetch` with date range
2. Filter for events likely needing prep:
   - Duration > 30 minutes (shorter meetings often don't need prep)
   - Not all-day events
   - Not personal time blocks (check title for "Focus", "Lunch", "Break", etc.)
   - Keywords suggest business: "meeting", "call", "demo", "presentation", "interview", "review", "1:1"
3. Sort by date (soonest first)

### Checking for Existing Preparation

**For each qualifying event**:

1. **Search projects**: Look in `4_Projects/` for files mentioning:
   - Event title (fuzzy match)
   - Key attendees/companies mentioned
   - Related keywords

2. **Search next actions**: Look in `5_GTD/next-actions.md` for tasks mentioning:
   - Event title
   - Event date
   - Attendees

3. **Classify**:
   - ✅ **Has prep**: Found project + next action(s)
   - ⚠️ **Needs prep**: No project or actions found

### Suggesting Preparation Tasks

**By event type** (infer from title/context):

**Client meetings/demos**:
- Review account history
- Prepare demo environment
- Update proposal/materials
- Research attendees
- Prepare Q&A responses

**1:1 meetings**:
- Review previous 1:1 notes
- Prepare discussion topics
- Gather feedback to share
- Update status on ongoing items

**Presentations/talks**:
- Build/update slides
- Practice delivery
- Prepare Q&A
- Test technical setup

**Interviews (conducting)**:
- Review candidate background
- Prepare interview questions
- Coordinate with interview panel
- Set up interview logistics

**Reviews (performance, project, etc.)**:
- Gather metrics/data
- Prepare status update
- Identify blockers/risks
- Prepare recommendations

**Unknown/Generic meetings**:
- Review agenda (if available)
- Prepare discussion topics
- Research context/background

### Creating Prep Projects

**When user confirms they want prep help**:

1. **Create project file**:
```markdown
---
type: project
status: active
created: YYYY-MM-DD
tags: [project, meeting-prep]
---

# Prep for [Event Name]

## Desired Outcome
Be fully prepared for [Event Name] on [Date]

## Event Details
- **Date**: [Date and Time]
- **Duration**: [Duration]
- **Attendees**: [List if known]
- **Location**: [Location/Link]

## Next Actions
- [ ] [First prep task] @computer #energy-medium #time-15m

## Notes
Calendar event: [Event Title] on [Date]

## Related
```

2. **Add first next action** to `5_GTD/next-actions.md` with:
   - Task description
   - Inferred context (@computer for most prep work)
   - Suggested energy/time metadata
   - Link back to project: `[[4_Projects/Prep for Event Name]]`

### Time-Sensitive Recommendations

**Urgency levels**:

- **7+ days away**: "You have time - want to schedule prep for later this week?"
- **3-6 days away**: "Coming up soon. Good time to start preparing."
- **1-2 days away**: "This is soon! Want to block time today for prep?"
- **< 24 hours**: "This is tomorrow! Need urgent prep time?"

**Scheduling suggestions**:
- Offer to use Workflow 6 (Schedule Time for Task) to block calendar time
- For urgent prep (< 2 days), suggest scheduling same day
- For advance prep (> 3 days), suggest scheduling 2-3 days before event

### Example Output

```
Here are your upcoming events that might need preparation:

**Wednesday, Nov 13 at 2:00 PM** - AI Alliance Meeting (1 hour)
  ✅ Found project: "Prep For AI Alliance Meeting"
  ✅ Next action: "Review meeting minutes" @computer #energy-medium #time-15m
  You're all set for this one!

**Thursday, Nov 14 at 10:00 AM** - Client Demo with Acme Corp (1 hour)
  ⚠️ No prep found. This is a client demo - suggested prep:
    - Review demo script and test environment
    - Prepare Q&A responses for common questions
    - Review Acme Corp account history
  Want me to create a prep project? (2 days away - good time to prepare)

**Friday, Nov 15 at 3:00 PM** - 1:1 with Sarah (30 min)
  ⚠️ No prep found. For 1:1s, you might want to:
    - Review previous 1:1 notes
    - Prepare discussion topics
  Quick 15-minute task - want me to add it?
```

### Integration with Other Workflows

**Proactive reminders**:
- During Workflow 1 ("What should I work on?"): Suggest running event prep scan if not done in 2+ days
- During Workflow 8 ("What's my day look like?"): Mention upcoming events with missing prep

**Connecting prep to scheduling**:
- After creating prep tasks, offer Workflow 6 to schedule them
- Consider event timing when suggesting prep work schedule
- Block prep time before the event, leaving buffer

## Fantastical Integration

### Overview

Fantastical provides fast, natural-language event creation via AppleScript and URL schemes. Use it for quick calendar blocks where structured metadata (notes, availability, Obsidian links) isn't needed.

### Creating Events via AppleScript

**Basic syntax (opens editor for review):**
```bash
osascript -e 'tell application "Fantastical" to parse sentence "Team lunch Friday at noon at Pizzeria Vetri"'
```

**Immediate creation (skips UI):**
```bash
osascript -e 'tell application "Fantastical" to parse sentence "Block: Deep work 8am to 11am tomorrow" with add immediately'
```

Fantastical's natural language parser handles:
- Dates and times: "tomorrow at 2pm", "next Monday 9am to 11am", "March 15 all day"
- Locations: "at Comcast Center", "at 1800 Arch St"
- Duration: "for 2 hours", "from 9am to 7pm"
- Recurrence: "every Tuesday at 3pm" (parsed by Fantastical, not scriptable via iMCP)

### Creating Events via URL Scheme

```
x-fantastical3://parse?s=EVENT_TEXT&n=NOTES&calendarName=CALENDAR&add=1
```

| Parameter | Purpose | Required |
|-----------|---------|----------|
| `s` | Natural-language event description | Yes |
| `n` | Notes to attach | No |
| `calendarName` | Target calendar | No (uses default) |
| `add` | `1` to create immediately | No (opens editor if omitted) |

**Example:**
```
x-fantastical3://parse?s=Dentist%20appointment%20Thursday%20at%203pm&calendarName=Personal&add=1
```

### Navigating the Calendar

Open Fantastical to a specific date (useful after presenting daily schedule):
```bash
open "x-fantastical3://show/mini/2026-03-10"
```

Open full calendar view:
```bash
open "x-fantastical3://show/calendar"
```

### When to Use Fantastical vs iMCP vs Reclaim

| Scenario | Tool | Rationale |
|----------|------|-----------|
| Quick block from natural language | **Fantastical** | Simplest, no parameter formatting needed |
| Event with notes/metadata/Obsidian links | **iMCP** | Full field control |
| Event needing availability flag (busy/free) | **iMCP** | Fantastical can't set this programmatically |
| Auto-schedule flexible task | **Reclaim** | AI finds optimal slot |
| Read/update/delete existing events | **iMCP** | Fantastical is write-only via script |
| Navigate user to calendar date | **Fantastical** URL scheme | Opens native UI |

### Fantastical Limitations

- **Write-only**: Cannot read, update, or delete events via AppleScript or URL scheme
- **No structured fields**: Cannot programmatically set availability, add attendees, or attach rich notes
- **Calendar selection**: Uses default calendar unless `calendarName` parameter is provided
- **No return value**: AppleScript call doesn't return the created event's identifier

## Best Practices

### Do's
✓ Always run `date` first to get current time before any time comparisons
✓ Always check calendar before suggesting tasks
✓ Respect user's energy level self-assessment
✓ Prioritize morning for #energy-high tasks
✓ Include buffer time (don't schedule back-to-back all day)
✓ Link calendar events to Obsidian for context
✓ Suggest time blocking for important/long tasks
✓ Proactively scan for upcoming meetings needing prep
✓ Create prep projects 2-7 days before events

### Don'ts
✗ Don't assume you know the current time - always run `date` first
✗ Don't override calendar appointments to fit tasks
✗ Don't suggest tasks that don't fit available time
✗ Don't schedule deep work in afternoon if morning available
✗ Don't create calendar events without user confirmation
✗ Don't ignore recurring calendar events
✗ Don't suggest "just a little over" time estimates
✗ Don't suggest prep for very short meetings (< 30 min) unless specifically requested
✗ Don't create duplicate prep projects if one already exists

## Apple Reminders Integration

### Overview
Apple Reminders integration via iMCP enables processing of Siri-captured tasks alongside Obsidian inbox items.

### Use Case: Siri Quick Capture
**User workflow:**
1. Throughout day: "Hey Siri, remind me to [task]"
2. Tasks accumulate in "Todo List" reminder list
3. During inbox processing: Fetch and process all reminders
4. Convert to GTD next actions, projects, or someday/maybe

### Using iMCP Reminders Tools

**1. Fetching Reminders for Inbox Processing**

**Tool**: `mcp__iMCP__reminders_fetch`

**Basic usage**:
```
mcp__iMCP__reminders_fetch({
  lists: ["Todo List"],
  completed: false
})
```

**Parameters**:
- `lists`: Array of list names, use `["Todo List"]` as default
- `completed`: Set to `false` to get only incomplete reminders
- `query`: Optional text search within reminder titles
- `start`/`end`: Optional date range filtering

**2. Listing Available Reminder Lists**

**Tool**: `mcp__iMCP__reminders_lists`

Use this on first run or if "Todo List" not found:
```
mcp__iMCP__reminders_lists()
```

Returns all reminder lists. Verify "Todo List" exists or ask user which list to use.

**3. Creating Reminders (Rarely Used)**

**Tool**: `mcp__iMCP__reminders_create`

Generally prefer Obsidian Quick Capture (Workflow 3), but available if needed:
```
mcp__iMCP__reminders_create({
  list: "Todo List",
  title: "Task description",
  notes: "Additional details",
  due: "2025-11-15T09:00:00Z"  // Optional (UTC)
})
```

### Inbox Processing with Reminders

**Modified Workflow 2 Process:**

1. **Gather from both sources**:
   - Obsidian: Read `1_inbox/` files with `#task/inbox` tag
   - Reminders: Fetch incomplete from "Todo List"
   - Combine and count: "Found 4 Obsidian items + 3 reminders (7 total)"

2. **Process each item** through standard GTD workflow:
   - Present with suggested rewrite
   - Determine if actionable
   - Route to next-actions, projects, someday/maybe, or reference
   - Clean up source

3. **Source cleanup**:
   - **Obsidian items**: Delete file from `1_inbox/`
   - **Reminders**: Cannot be marked complete via iMCP
     - Inform user: "Processed '[title]' - please mark complete via Reminders app or Siri"
     - Provide Siri command: "Mark [title] as complete in Todo List"

### Completing Reminders

**Tool**: `mcp__iMCP__reminders_complete`

Reminders CAN be marked complete via iMCP.

**Usage**:
```
mcp__iMCP__reminders_complete({
  identifiers: ["reminder-uuid-1", "reminder-uuid-2"]
})
```

**Parameters**:
- `identifiers`: Array of reminder UUID strings (from `reminders_fetch`)

**Example workflow**:
```
1. Fetch reminders: mcp__iMCP__reminders_fetch({ lists: ["Todo"] })
2. Process each reminder through GTD workflow
3. Mark complete: mcp__iMCP__reminders_complete({ identifiers: ["uuid-here"] })
```

**Example output**:
```
Processed 3 reminders:
- "Buy groceries" → Added to Todoist Next Actions ✓
- "Call dentist" → Added to Todoist Next Actions ✓
- "Research vacation spots" → Added to Someday/Maybe ✓

All reminders marked complete in Apple Reminders.
```

### Best Practices

**Do's:**
✓ Always fetch reminders during inbox processing
✓ Process reminders with same GTD rigor as Todoist items
✓ Mark reminders complete after processing via `reminders_complete`
✓ Use the reminder's `identifier` (UUID) for completion

**Don'ts:**
✗ Don't skip reminders - they're captured intentions
✗ Don't leave processed reminders incomplete in Apple Reminders
✗ Don't forget to collect identifiers during processing for batch completion

## Integration with GTD Workflows

### Workflow 1: "What Should I Be Working On?"
- **Before**: Asked user for available time
- **Now**: Automatically checks calendar, calculates free blocks
- **Benefit**: Suggestions always fit real available time

### Workflow 2: "Process Inbox"
- **Before**: Only processed Obsidian `1_inbox/` files
- **Now**: Fetches Apple Reminders "Todo List" + Obsidian inbox
- **Benefit**: Unified GTD processing for all capture sources

### Workflow 6: "Schedule Time for Task"
- **New workflow**: Creates calendar events for tasks
- **Links**: Obsidian ↔ Calendar for seamless flow
- **Tracks**: Adds 📅 emoji or note to next-actions.md

### Workflow 7: "Find Deep Work Time"
- **New workflow**: Proactive deep work scheduling
- **Scans**: Whole week for optimal blocks
- **Matches**: Longest tasks to best time slots

### Workflow 8: "What's My Day Look Like?"
- **New workflow**: Daily overview with task suggestions
- **Shows**: Events + free blocks + recommendations
- **Helps**: Morning planning and daily prioritization

### Workflow 9: "Prep for Upcoming Events"
- **New workflow**: Proactive meeting preparation
- **Scans**: Next 7 days for events needing prep
- **Identifies**: Meetings without preparation tasks
- **Creates**: Projects and next actions for event prep
- **Schedules**: Optional time blocking for preparation work

## Reclaim.ai Integration

### Overview

Reclaim.ai provides AI-powered auto-scheduling, habits, focus time protection, and time tracking. Use iMCP for all calendar reading and specific-time event creation; use Reclaim only for its unique scheduling capabilities.

### When to Use Each Tool

| Task | iMCP | Reclaim |
|------|------|---------|
| Read calendar events | ✓ | |
| Create event at specific time | ✓ | |
| Find deep work blocks | ✓ | |
| Auto-schedule task (flexible timing) | | ✓ |
| Recurring time blocks (habits) | | ✓ |
| Focus time protection | | ✓ |
| Time tracking | | ✓ |

### Auto-Scheduling Tasks

Instead of manually finding time slots and creating calendar events, send tasks to Reclaim:

**From Todoist task to Reclaim:**
```
mcp__reclaim__create_task with:
  title: "Update EyeGuide video API",
  duration_minutes: 120,
  priority: "P1",
  due_date: "2026-01-10",
  min_chunk_size_minutes: 30
```

Reclaim will:
1. Analyze your calendar for available time
2. Find the optimal slot based on priority and energy
3. Create a calendar event automatically
4. Reschedule if conflicts arise

### Energy-Aware Scheduling

Map GTD energy levels to Reclaim scheduling behavior:

**#energy-high tasks:**
- Use `snooze_until` to prefer morning slots
- Set higher priority (P1/P2)
- Example:
  ```
  mcp__reclaim__create_task with:
    title: "Deep work: API design",
    duration_minutes: 120,
    priority: "P1",
    snooze_until: "2026-01-06T06:00:00Z"
  ```

**#energy-medium tasks:**
- Default scheduling (Reclaim chooses best time)
- Priority P2/P3

**#energy-low tasks:**
- Can fill gaps and end-of-day slots
- Priority P3/P4
- Good candidates for chunking into smaller pieces

### Reclaim Habits for GTD Routines

Use Reclaim habits for recurring GTD activities:

**Weekly Review:**
```
mcp__reclaim__create_habit with:
  title: "GTD Weekly Review",
  ideal_time: "14:00",
  duration_min_mins: 45,
  duration_max_mins: 90,
  frequency: "WEEKLY",
  ideal_days: ["FRIDAY"],
  defense_aggression: "HIGH"
```

**Daily Inbox Processing:**
```
mcp__reclaim__create_habit with:
  title: "Process Inbox",
  ideal_time: "09:00",
  duration_min_mins: 15,
  duration_max_mins: 30,
  frequency: "DAILY",
  event_type: "SOLO_WORK"
```

### Focus Time Protection

Configure Reclaim to protect deep work time:

```
mcp__reclaim__get_focus_settings

mcp__reclaim__update_focus_settings with:
  settings_id: 123,
  min_duration_mins: 90,
  ideal_duration_mins: 120,
  defense_aggression: "HIGH"
```

### Time Tracking

Track time spent on tasks through Reclaim:

**Start working:**
```
mcp__reclaim__start_task with:
  task_id: 12345
```

**Stop working:**
```
mcp__reclaim__stop_task with:
  task_id: 12345
```

**Log time manually:**
```
mcp__reclaim__add_time_to_task with:
  task_id: 12345,
  minutes: 45,
  notes: "Completed first milestone"
```

### Completing Reclaim Tasks

When marking tasks complete, update both systems:

```
# Complete in Todoist
mcp__todoist__complete-tasks with:
  ids: ["todoist-task-id"]

# Complete in Reclaim
mcp__reclaim__mark_task_complete with:
  task_id: 12345
```

### Viewing Scheduled Tasks

Check what Reclaim has scheduled:

```
mcp__reclaim__list_tasks with:
  status: "SCHEDULED",
  limit: 20
```

### Best Practices for Reclaim + GTD

**Do's:**
✓ Use Reclaim for tasks with flexible timing
✓ Let Reclaim handle recurring GTD habits (weekly review, daily planning)
✓ Mark tasks in both Todoist and Reclaim when complete
✓ Use chunking for long tasks that can be split
✓ Set appropriate priority to influence scheduling

**Don'ts:**
✗ Don't create Reclaim tasks for items that need specific times (use iMCP)
✗ Don't duplicate every Todoist task in Reclaim (only scheduled ones)
✗ Don't forget to mark Reclaim tasks complete when done
✗ Don't set all tasks as P1 (defeats prioritization)
