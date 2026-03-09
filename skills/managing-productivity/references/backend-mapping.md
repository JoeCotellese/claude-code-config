# Backend Integration Mapping

This document details how the productivity system's backends (Todoist and Reclaim.ai) are configured and used via MCP tools.

## Todoist MCP Implementation

### GTD List Structure

Use Todoist projects to represent GTD lists:
- **inbox** - Use Todoist's built-in Inbox (projectId: "inbox")
- **next-actions** - Custom project "Next Actions"
- **projects** - Custom project "Projects" (stores project definitions)
- **waiting-for** - Custom project "Waiting For"
- **someday-maybe** - Custom project "Someday/Maybe"
- **reference** - Use label `@reference` (tasks can live in any project)

**Note:** Project IDs must be obtained once via `find-projects` and can be cached or looked up dynamically.

### Metadata Mapping

**Context tags:** `@home`, `@work`, `@computer`, `@phone`, `@errands`, `@anywhere` → Todoist labels

**Energy tags:** `#energy-high`, `#energy-medium`, `#energy-low` → Todoist labels

**Time tags:**
- `#time-5m` → duration: "5m"
- `#time-15m` → duration: "15m"
- `#time-30m` → duration: "30m"
- `#time-1h` → duration: "1h"
- `#time-2h` → duration: "2h"

**Priority:** Map to Todoist priorities
- Urgent → p1 (highest)
- Important → p2 (high)
- Normal → p3 (medium)
- Low → p4 (lowest/default)

### Direct MCP Tool Usage

The Todoist backend uses MCP tools directly. Here's how each abstract operation maps:

#### 1. capture
**Operation:** Add new item to inbox

**Direct Call:**
```
mcp__todoist__add-tasks with:
  tasks: [{
    content: "task description",
    projectId: "inbox"
  }]
```

**With metadata:**
```
mcp__todoist__add-tasks with:
  tasks: [{
    content: "task description",
    projectId: "inbox",
    labels: ["@computer", "#energy-medium"],
    duration: "30m"
  }]
```

---

#### 2. list_inbox
**Operation:** Get all items in inbox

**Direct Call:**
```
mcp__todoist__find-tasks with:
  projectId: "inbox",
  limit: 50
```

---

#### 3. list_by_context
**Operation:** Get items from specific GTD list

**Direct Call:**
```
# Step 1: Look up project ID by name
mcp__todoist__find-projects with:
  search: "Next Actions",  # or "Projects", "Waiting For", "Someday/Maybe"
  limit: 1

# Step 2: Use project ID from results
mcp__todoist__find-tasks with:
  projectId: "<project-id-from-step-1>",
  limit: 50
```

**Note:** Project IDs can be cached after first lookup

---

#### 4. search
**Operation:** Find items by keyword

**Direct Call:**
```
mcp__todoist__find-tasks with:
  searchText: "search query",
  limit: 20
```

**With GTD list filter:**
```
# First lookup project ID (see list_by_context)
mcp__todoist__find-tasks with:
  searchText: "search query",
  projectId: "<project-id>",
  limit: 20
```

---

#### 5. add_metadata
**Operation:** Add tags/metadata to an item (context, energy, time)

**Direct Call:**
```
mcp__todoist__update-tasks with:
  tasks: [{
    id: "task-id",
    labels: ["@computer", "#energy-medium"],  # appends to existing
    duration: "30m"
  }]
```

**Note:** Labels are appended, not replaced. To replace, first fetch task, then update with complete label list.

---

#### 6. move_to_list
**Operation:** Move item between GTD lists

**Direct Call:**
```
# Lookup target project ID first (see list_by_context)
mcp__todoist__update-tasks with:
  tasks: [{
    id: "task-id",
    projectId: "<target-project-id>"
  }]
```

---

#### 7. mark_complete
**Operation:** Archive or mark item as done

**Direct Call:**
```
mcp__todoist__complete-tasks with:
  ids: ["task-id"]
```

---

#### 8. get_item
**Operation:** Get details of a single item

**Direct Call:**
```
mcp__todoist__find-tasks with:
  searchText: "exact task title or partial match",
  limit: 1
```

**Note:** Todoist MCP doesn't have direct "get by ID". Use search with exact title or keep task details from previous operations.

---

#### 9. filter_by_metadata
**Operation:** Filter items by multiple criteria (context + energy + time)

**Direct Call:**
```
# Lookup project ID first (see list_by_context)
mcp__todoist__find-tasks with:
  projectId: "<project-id>",
  labels: ["@computer", "#energy-medium"],
  labelsOperator: "and",
  limit: 50
```

**Time filtering:** Todoist can't filter by duration in query. Filter results by checking `duration` field in response.

**Example with time filter:**
```
# 1. Call find-tasks with label filters
# 2. Post-process results to keep only tasks with duration: "30m"
```

---

## Implementation Notes for Todoist

### Project Setup Required

Before using Todoist backend, ensure these projects exist:
1. Next Actions
2. Projects
3. Waiting For
4. Someday/Maybe

Create via:
```
mcp__todoist__add-projects with:
  projects: [
    {"name": "Next Actions"},
    {"name": "Projects"},
    {"name": "Waiting For"},
    {"name": "Someday/Maybe"}
  ]
```

### Project ID Lookup

GTD project names map as follows:
- `inbox` → projectId: "inbox" (special Todoist inbox, no lookup needed)
- `next-actions` → Look up "Next Actions" project
- `projects` → Look up "Projects" project
- `waiting-for` → Look up "Waiting For" project
- `someday-maybe` → Look up "Someday/Maybe" project

**To cache project IDs** (recommended for performance):
1. On first use, call `mcp__todoist__find-projects` with search: "Next Actions" etc.
2. Store the returned project IDs for the session
3. Reuse cached IDs for subsequent operations

### Label Management

All metadata labels should be created in Todoist before use. Create them via Todoist web UI or during initial setup.

Required labels:
- Context: `@home`, `@work`, `@computer`, `@phone`, `@errands`, `@anywhere`
- Energy: `#energy-high`, `#energy-medium`, `#energy-low`
- Reference: `@reference`

Time tags use the duration field, not labels.

### Duration vs Time Tags

Todoist's duration field supports: "5m", "15m", "30m", "1h", "2h", etc.

Map time tags directly:
- `#time-5m` → duration: "5m"
- `#time-1h` → duration: "1h"

### Due Date Natural Language

The `dueString` parameter accepts specific natural language patterns. The API will reject ambiguous phrases.

**Works:**
- Day names: `"Monday"`, `"Friday"`, `"next Tuesday"`
- Relative: `"tomorrow"`, `"today"`, `"next week"`
- Specific dates: `"Jan 15"`, `"January 15"`, `"2026-01-15"`
- Time combos: `"tomorrow at 9am"`, `"Friday at 3pm"`
- Recurring: `"every Monday"`, `"every weekday at 9am"`

**Doesn't work (returns 400 Bad Request):**
- `"this week"` - ambiguous, no specific day
- `"soon"`, `"later"` - too vague
- `"sometime tomorrow"` - unnecessary qualifier

**Best practice:** Use explicit day names or dates. When in doubt, use `"tomorrow"` or a specific day like `"Friday"`.

### Filtering Limitations

Todoist MCP filtering:
- Can filter by labels with AND/OR operators
- Can filter by project
- Cannot directly filter by duration in search

For time-based filtering, fetch results and post-process by duration field.

### Data Return Format

Todoist MCP returns structured data:
1. Call MCP tool
2. Format results for display
3. Return structured data to skill

---

## Reclaim.ai MCP Implementation

### Overview

Reclaim.ai is an AI-powered calendar scheduling tool that automatically finds optimal time slots for tasks, habits, and focus time. Unlike manual calendar blocking (iMCP), Reclaim:

- **Auto-schedules tasks** into available calendar slots
- **Reschedules automatically** when conflicts arise
- **Respects existing calendar** events and meetings
- **Optimizes for energy** by scheduling high-priority tasks in preferred time windows

**Best used for:** Tasks that need to happen but timing is flexible. Reclaim finds the best slot so you don't have to.

**Use iMCP instead when:** You need a specific time slot (e.g., "block 9am tomorrow for this call").

### GTD Integration Model

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Todoist      │     │   Reclaim.ai    │     │    Calendar     │
│  (GTD System)   │────▶│  (Scheduler)    │────▶│   (Execution)   │
│                 │     │                 │     │                 │
│ - Next Actions  │     │ - Auto-schedule │     │ - Time blocks   │
│ - Metadata      │     │ - Reschedule    │     │ - Reminders     │
│ - Projects      │     │ - Time tracking │     │ - Visibility    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Metadata Mapping: Todoist → Reclaim

| Todoist | Reclaim Task | Notes |
|---------|--------------|-------|
| Task content | `title` | Direct mapping |
| `duration: "2h"` | `duration_minutes: 120` | Convert to minutes |
| `p1` (highest) | `priority: "P1"` | Same scale! |
| `p2` (high) | `priority: "P2"` | |
| `p3` (medium) | `priority: "P3"` | |
| `p4` (lowest) | `priority: "P4"` | |
| `#energy-high` | `snooze_until: <morning>` | Schedule in AM window |
| Due date | `due_date` | ISO format YYYY-MM-DD |
| Duration chunks | `min_chunk_size_minutes` | For splittable tasks |

### Reclaim MCP Tools

#### Task Management

**1. create_task - Create auto-scheduled task**
```
mcp__reclaim__create_task with:
  title: "Update EyeGuide video API",
  duration_minutes: 120,
  priority: "P1",
  due_date: "2026-01-10",
  min_chunk_size_minutes: 30,  # Can be split into 30min chunks
  max_chunk_size_minutes: 120  # Or done in one 2hr block
```

**2. list_tasks - Get active Reclaim tasks**
```
mcp__reclaim__list_tasks with:
  status: "NEW,SCHEDULED,IN_PROGRESS",
  limit: 50
```

**3. update_task - Modify existing task**
```
mcp__reclaim__update_task with:
  task_id: 12345,
  duration_minutes: 90,
  priority: "P2"
```

**4. mark_task_complete - Complete a task**
```
mcp__reclaim__mark_task_complete with:
  task_id: 12345
```

**5. start_task / stop_task - Time tracking**
```
mcp__reclaim__start_task with:
  task_id: 12345

mcp__reclaim__stop_task with:
  task_id: 12345
```

**6. add_time_to_task - Log time manually**
```
mcp__reclaim__add_time_to_task with:
  task_id: 12345,
  minutes: 45,
  notes: "Completed API integration"
```

#### Habits (Recurring Auto-Scheduled Blocks)

**9. create_habit - Create recurring time block**
```
mcp__reclaim__create_habit with:
  title: "Morning Focus Time",
  ideal_time: "08:00",
  duration_min_mins: 60,
  duration_max_mins: 120,
  frequency: "WEEKLY",
  ideal_days: ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
  event_type: "FOCUS",
  defense_aggression: "HIGH"  # Protect this time
```

**10. list_habits - Get all habits**
```
mcp__reclaim__list_habits
```

#### Focus Time

**11. get_focus_settings - Check focus time config**
```
mcp__reclaim__get_focus_settings
```

**12. update_focus_settings - Modify focus protection**
```
mcp__reclaim__update_focus_settings with:
  settings_id: 123,
  min_duration_mins: 60,
  ideal_duration_mins: 120,
  defense_aggression: "HIGH"
```

### GTD Workflow Integration

#### Schedule Task via Reclaim (Workflow 6 Alternative)

**When to use Reclaim vs iMCP:**

| Scenario | Use Reclaim | Use iMCP |
|----------|-------------|----------|
| "Schedule this task sometime this week" | ✓ | |
| "Block 9am tomorrow for this" | | ✓ |
| Task has flexible timing | ✓ | |
| Task needs specific slot | | ✓ |
| Want auto-reschedule on conflicts | ✓ | |
| Creating a one-time event | | ✓ |

**Reclaim Scheduling Process:**

1. **Find task in Todoist**
   ```
   mcp__todoist__find-tasks with:
     searchText: "task name",
     projectId: "6fHPx2qmvwhq5x4X"  # Next Actions
   ```

2. **Extract metadata and map to Reclaim**
   - Duration → `duration_minutes`
   - Priority (p1-p4) → `priority` (P1-P4)
   - Due date → `due_date`
   - Energy level → Influences scheduling preferences

3. **Create Reclaim task**
   ```
   mcp__reclaim__create_task with:
     title: "[task content from Todoist]",
     duration_minutes: 120,
     priority: "P1",
     due_date: "2026-01-10",
     min_chunk_size_minutes: 30
   ```

4. **Update Todoist task with Reclaim reference**
   ```
   mcp__todoist__update-tasks with:
     tasks: [{
       id: "todoist-task-id",
       description: "📅 Auto-scheduled via Reclaim\n\n[existing description]"
     }]
   ```

5. **Confirm to user**
   ```
   I've sent "[task]" to Reclaim for auto-scheduling. It will find the best
   2-hour block based on your calendar availability. The task will appear on
   your calendar once scheduled.
   ```

#### Energy-Based Scheduling with Reclaim

For `#energy-high` tasks, use `snooze_until` to ensure morning scheduling:

```
mcp__reclaim__create_task with:
  title: "Deep work: API design",
  duration_minutes: 120,
  priority: "P1",
  snooze_until: "2026-01-06T06:00:00Z"  # Don't schedule before 6am tomorrow
```

**Energy mapping strategy:**
- `#energy-high` → Schedule in morning (6am-12pm window preferred)
- `#energy-medium` → Any available slot
- `#energy-low` → Can fill gaps, end of day

### Syncing Todoist ↔ Reclaim

**One-way sync (recommended):**
- Todoist is the source of truth for GTD
- Reclaim is used for scheduling specific tasks
- Completion in either system should update both

**Completion workflow:**
1. When marking complete in Todoist: Also call `mcp__reclaim__mark_task_complete`
2. When tracking time in Reclaim: Note in Todoist description

**Avoiding duplicates:**
- Only send tasks to Reclaim when user explicitly requests scheduling
- Add "📅 Reclaim" marker to Todoist task description
- Before creating Reclaim task, check if one already exists with same title

### Reclaim Habits for GTD

**Use Reclaim habits for recurring GTD activities:**

| GTD Activity | Reclaim Habit |
|--------------|---------------|
| Weekly Review | `frequency: "WEEKLY"`, `ideal_days: ["FRIDAY"]`, `duration: 60min` |
| Daily Planning | `frequency: "DAILY"`, `ideal_time: "08:00"`, `duration: 15min` |
| Inbox Processing | `frequency: "DAILY"`, `ideal_time: "09:00"`, `duration: 30min` |

**Example: Create Weekly Review habit**
```
mcp__reclaim__create_habit with:
  title: "GTD Weekly Review",
  ideal_time: "14:00",
  duration_min_mins: 45,
  duration_max_mins: 90,
  frequency: "WEEKLY",
  ideal_days: ["FRIDAY"],
  event_type: "SOLO_WORK",
  defense_aggression: "HIGH",
  description: "Review projects, process loose ends, plan next week"
```

---

