# Workflow 6: Schedule Time for Task

## Trigger Phrases
- "Schedule [task]"
- "Block time for [task]"
- "Put [task] on my calendar"
- "Add [task] to calendar"
- "Auto-schedule [task]" (triggers Reclaim path)

## Scheduling Options

This workflow offers two scheduling approaches:

| Approach | Best For | Tool |
|----------|----------|------|
| **Manual** (iMCP) | Specific time slots, one-time events | `mcp__iMCP__events_create` |
| **Auto** (Reclaim) | Flexible timing, wants AI to find optimal slot | `mcp__reclaim__create_task` |

## Process

### Step 1: Find the Task

Search Next Actions for the task by name/description:
```
mcp__todoist__find-tasks with:
  searchText: "task name",
  projectId: "6fHPx2qmvwhq5x4X"  # Next Actions
```

### Step 2: Extract Task Metadata

- Duration from duration field (15m → 15 minutes, 2h → 2 hours)
- Energy level from labels (`#energy-high`, `#energy-medium`, `#energy-low`)
- Context from labels (`@computer`, `@home`, etc.)
- Priority from Todoist priority (p1-p4)
- Due date if set

### Step 3: Ask Scheduling Preference

```
How would you like to schedule "[task name]"?

1. **Auto-schedule** - Let Reclaim find the best time based on your calendar
2. **Manual** - Pick a specific time slot yourself

(Auto-schedule is great for flexible tasks; manual is better if you need a specific time)
```

---

## Path A: Auto-Schedule via Reclaim

### A1. Map Todoist Metadata to Reclaim

| Todoist | Reclaim |
|---------|---------|
| Duration `2h` | `duration_minutes: 120` |
| Priority `p1` | `priority: "P1"` |
| Due date | `due_date: "YYYY-MM-DD"` |
| `#energy-high` | Consider `snooze_until` for morning |

**Duration conversion:**
- `5m` → 5
- `15m` → 15
- `30m` → 30
- `1h` → 60
- `2h` → 120

### A2. Create Reclaim Task

```
mcp__reclaim__create_task with:
  title: "[task content]",
  duration_minutes: 120,
  priority: "P1",
  due_date: "2026-01-10",
  min_chunk_size_minutes: 30,  # Optional: allow chunking
  max_chunk_size_minutes: 120
```

**For #energy-high tasks**, add snooze to prefer morning:
```
mcp__reclaim__create_task with:
  title: "[task content]",
  duration_minutes: 120,
  priority: "P1",
  snooze_until: "2026-01-06T06:00:00Z"  # Tomorrow 6am
```

### A3. Update Todoist Task with Reference

```
mcp__todoist__update-tasks with:
  tasks: [{
    id: "todoist-task-id",
    description: "📅 Auto-scheduled via Reclaim\n\n[existing description]"
  }]
```

### A4. Confirm

```
I've sent "[task name]" to Reclaim for auto-scheduling.

- Duration: 2 hours
- Priority: High (P1)
- Due: Friday, Jan 10

Reclaim will find the optimal time slot based on your calendar. The task
will appear on your calendar once scheduled. You can check Reclaim tasks
anytime with "show my Reclaim tasks".
```

---

## Path B: Manual Schedule via iMCP

### B1. Check Calendar Availability

Use iMCP to get today's and upcoming events:
```
mcp__iMCP__events_fetch with:
  start: "2026-01-05T00:00:00",
  end: "2026-01-12T23:59:59"
```

### B2. Find Free Blocks

Calculate free blocks that match task duration:
- For `#energy-high` tasks, prioritize morning/early morning (before noon, especially before 9am)
- For `#energy-low` tasks, any available time works
- For `#energy-medium` tasks, prefer mid-morning or afternoon

### B3. Present Available Slots

```
I found these available slots for "[task name]" (needs 2 hours):

**Today:**
- 9:00 AM - 11:00 AM (2 hours free)
- 2:30 PM - 5:00 PM (2.5 hours free)

**Tomorrow:**
- 8:00 AM - 10:00 AM (2 hours free) ⭐ Prime time

Since this is a #energy-high task, I'd recommend tomorrow at 8:00 AM.
Which slot works for you?
```

### B4. Create Calendar Event

```
mcp__iMCP__events_create with:
  calendar: "Personal",
  title: "[task name]",
  start: "2026-01-06T08:00:00",
  end: "2026-01-06T10:00:00",
  notes: "@computer #energy-high 2h\n\nTodoist: [task URL]",
  availability: "busy"
```

### B5. Update Todoist Task (Optional)

```
mcp__todoist__update-tasks with:
  tasks: [{
    id: "todoist-task-id",
    description: "📅 Scheduled: Mon Jan 6, 8-10am\n\n[existing description]"
  }]
```

### B6. Confirm

```
Scheduled "[task name]" for tomorrow (Monday) at 8:00 AM - 10:00 AM.

It's on your calendar and marked in Todoist. Good luck with it!
```

---

## Implementation Notes

### When Task Has No Duration
Ask user: "How long do you think this will take?"

Options: 15 minutes, 30 minutes, 1 hour, 2 hours, Other

### When No Slots Available Today
Automatically suggest tomorrow and next few days.

### Recurring Calendar Events
Avoid suggesting those time slots for manual scheduling.

### Priority Mapping
Both Todoist and Reclaim use p1-p4/P1-P4 scale:
- p1/P1 = Critical/Highest
- p2/P2 = High
- p3/P3 = Medium
- p4/P4 = Low/Default

### Chunking for Long Tasks
For tasks > 1 hour, consider allowing Reclaim to chunk:
```
min_chunk_size_minutes: 30,  # Can split into 30min blocks
max_chunk_size_minutes: 120  # Or do all at once
```

This lets Reclaim fit parts of the task into smaller gaps if no large block is available.

---

## Checking Reclaim Tasks

To see scheduled Reclaim tasks:
```
mcp__reclaim__list_tasks with:
  status: "SCHEDULED",
  limit: 20
```

To see personal events (scheduled tasks + habits):
```
mcp__reclaim__list_personal_events with:
  start: "2026-01-05T00:00:00Z",
  end: "2026-01-12T23:59:59Z"
```
