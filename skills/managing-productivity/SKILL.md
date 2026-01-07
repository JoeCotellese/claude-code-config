---
name: managing-productivity
description: Help manage productivity using a hybrid GTD + Energy/Time filtering system in Todoist with calendar integration. This skill should be used when the user asks "what should I be working on?", wants to process their inbox, needs to capture tasks, asks about project status, wants to view their schedule, needs to block time for tasks, wants to check upcoming meetings for preparation needs, or requests help with task management and productivity. The skill guides GTD-style task clarification, adds context/energy/time metadata to tasks, filters suggestions based on current context and actual calendar availability, can schedule tasks on the calendar, and proactively identifies upcoming calendar events that need preparation.
---

# Managing Productivity (Todoist Edition)

## Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Workflows](#core-workflows)
- [Metadata System](#metadata-system)
- [File Operations](#file-operations)
- [Conversation Style](#conversation-style)
- [Obsidian Integration](#obsidian-integration)
- [References](#references)

## Overview

This skill implements a hybrid productivity system combining GTD (Getting Things Done) methodology with energy/time-based execution filtering and calendar integration.

| Component | Purpose |
|-----------|---------|
| **Todoist** (via MCP) | Task execution - inbox, next actions, waiting for, someday/maybe |
| **Reminders** (via iMCP) | Quick capture inbox, processed into Todoist |
| **Calendar** (via iMCP) | Availability checking, manual time blocking, meeting prep |
| **Reclaim.ai** (via MCP) | Auto-scheduling tasks, habits, focus time protection |
| **Email** (via zerolib-email MCP) | Email search, reading, sending, and management |
| **Obsidian** | Project documentation and next action backlogs |

**Key Design Principle:** Todoist is the *execution layer* (1-2 active tasks), Obsidian is the *planning layer* (full project backlogs).

### Inboxes for Inbox Zero

The system tracks multiple inboxes that should be processed to zero:

| Inbox | Location | How to Check |
|-------|----------|--------------|
| **Todoist Inbox** | Todoist project `6CrffChVJmwxG79h` | `mcp__todoist__find-tasks` with projectId |
| **Reminders Todo** | Apple Reminders "Todo List" | `mcp__iMCP__reminders_fetch` with lists: ["Todo List"] |

When user asks to "process inbox" or "check inboxes", check ALL tracked inboxes and report counts.

## System Architecture

### Todoist Backend

**GTD Project Structure:**
- **Inbox** (ID: `6CrffChVJmwxG79h`) - Capture area for new items
- **Next Actions** (ID: `6fHPx2qmvwhq5x4X`) - Single, physical, actionable tasks (limit 1-2)
- **Projects** (ID: `6fHPx2qMxx45cVm3`) - Multi-step outcomes
- **Waiting For** (ID: `6fGQg8Mp7g5g8J9C`) - Tasks blocked on others
- **Someday/Maybe** (ID: `6fHPx2qjgv2CGjpP`) - Future possibilities

**Todoist MCP Tools:**
- `mcp__todoist__add-tasks` - Create tasks with metadata
- `mcp__todoist__find-tasks` - Search/filter tasks
- `mcp__todoist__update-tasks` - Modify existing tasks
- `mcp__todoist__complete-tasks` - Mark tasks complete
- `mcp__todoist__find-projects` - List projects
- `mcp__todoist__get-overview` - Get account overview

### Calendar Integration

Integrates with primary calendar via iMCP for:
- Automatic availability checking when suggesting tasks
- Calculating free blocks between meetings
- Blocking time on calendar for specific tasks
- Finding optimal time slots for deep work
- Prioritizing morning/early morning (before noon, especially before 9am) for high-energy tasks

### Reclaim.ai Integration

Integrates with Reclaim.ai via MCP for intelligent auto-scheduling:

**Task Scheduling:**
- `mcp__reclaim__create_task` - Auto-schedule a task into available time
- `mcp__reclaim__list_tasks` - View scheduled/active tasks
- `mcp__reclaim__mark_task_complete` - Complete a task
- `mcp__reclaim__start_task` / `mcp__reclaim__stop_task` - Time tracking

**Habits (Recurring Blocks):**
- `mcp__reclaim__create_habit` - Create recurring time blocks (e.g., Weekly Review)
- `mcp__reclaim__list_habits` - View configured habits

**Calendar Reading:**
- `mcp__reclaim__list_events` - Get calendar events
- `mcp__reclaim__list_personal_events` - Get Reclaim-managed events

**Focus Time:**
- `mcp__reclaim__get_focus_settings` - Check focus time configuration
- `mcp__reclaim__update_focus_settings` - Adjust focus time protection

**When to use Reclaim vs iMCP:**

| Scenario | Use |
|----------|-----|
| "Schedule this task sometime" | Reclaim (auto-finds best slot) |
| "Block 9am tomorrow" | iMCP (specific time) |
| Recurring GTD routines | Reclaim habits |
| One-time calendar event | iMCP |
| Check calendar availability | Either |

### Email Integration

Integrates with email via zerolib-email MCP for:
- Searching emails by sender, recipient, subject, or date range
- Reading email content and metadata
- Sending emails and replies with proper threading
- Managing attachments

**Default Account:** Use `"Home"` as the `account_name` for all email operations.

**Email MCP Tools:**
- `mcp__zerolib-email__list_available_accounts` - List configured email accounts
- `mcp__zerolib-email__list_emails_metadata` - Search/filter emails (returns email_id, subject, sender, recipients, date)
- `mcp__zerolib-email__get_emails_content` - Get full email body content by email_id
- `mcp__zerolib-email__send_email` - Send new emails or replies (supports threading via `in_reply_to`)
- `mcp__zerolib-email__delete_emails` - Delete emails by email_id
- `mcp__zerolib-email__download_attachment` - Download email attachments (requires explicit enable)

**Key Parameters for `list_emails_metadata`:**
- `account_name` - Email account name (e.g., "Home")
- `from_address` - Filter by sender (partial match)
- `to_address` - Filter by recipient
- `subject` - Filter by subject line
- `since` / `before` - Date range filtering (UTC datetime)
- `page` / `page_size` - Pagination

### Obsidian Vault

**Location:** `/Users/joec/obsidian-vault/`

```
obsidian-vault/
├── 4_Projects/                 # Project documentation AND next action backlogs
│   └── [ProjectName].md        # Contains: outcome, context, full next action queue
├── 2_Literature Notes/         # Reference material from external sources
├── 3_Permanent Notes/          # Distilled evergreen knowledge
└── Templates/                  # Note templates
```

**Division of Labor:**

| Location | Purpose | Content |
|----------|---------|---------|
| **Todoist Next Actions** | Execution focus | Only 1-2 tasks you're actively working on today |
| **Obsidian Project Notes** | Planning & backlog | Full next action lists per project (the queue) |
| **Todoist Projects** | Project index | Links to Obsidian project notes |
| **Todoist Waiting For** | Blocking awareness | Items blocked on others |

When you complete a Next Action in Todoist, prompt the user to "pull" the next action from the relevant Obsidian project note.

## Core Workflows

### 1. What Should I Be Working On?
**Triggers:** "What should I be working on?", "What should I do next?", "Suggest a task"

Check calendar availability, ask context/energy, query Next Actions with filters, present top 3-5 options.

**Details:** See [references/workflows/what-should-i-work-on.md](references/workflows/what-should-i-work-on.md)

### 2. Process Inbox
**Triggers:** "Let's process my inbox", "Help me organize my tasks", "Check inboxes"

Check ALL tracked inboxes (Todoist Inbox + Reminders Todo List), report counts, then process each. Apply GTD clarification, add metadata, move to appropriate list.

**Details:** See [references/workflows/process-inbox.md](references/workflows/process-inbox.md)

### 3. Quick Capture
**Triggers:** "Add task: [description]", "Capture: [description]", "Todo: [description]"

Fast capture to Inbox without clarification. Offer to process immediately or later.

**Details:** See [references/workflows/quick-capture.md](references/workflows/quick-capture.md)

### 4. Project Check-in
**Triggers:** "What's the status of [project]?", "Show me my projects"

Search Projects, show next actions, waiting-for items, and Obsidian documentation link. Detect stalled projects.

**Details:** See [references/workflows/project-checkin.md](references/workflows/project-checkin.md)

### 5. Mark Task Complete
**Triggers:** "Done with [task]", "I completed [task]", "Finished [task]"

Mark complete in Todoist, then prompt to pull next action from Obsidian backlog if project-related.

**Details:** See [references/workflows/mark-complete.md](references/workflows/mark-complete.md)

### 6. Schedule Time for Task
**Triggers:** "Schedule [task]", "Block time for [task]", "Put [task] on my calendar"

Find available calendar slots matching task duration/energy, create calendar event.

**Details:** See [references/workflows/schedule-time.md](references/workflows/schedule-time.md)

### 7. Find Deep Work Time
**Triggers:** "When can I do deep work?", "Find time for focused work"

Find 2+ hour blocks in upcoming week, prioritize morning slots, suggest matching #energy-high tasks.

**Details:** See [references/workflows/find-deep-work.md](references/workflows/find-deep-work.md)

### 8. What's My Day Look Like?
**Triggers:** "What's my schedule today?", "Show me my day", "What meetings do I have?"

Present chronological overview with free blocks and task suggestions for each slot.

**Details:** See [references/workflows/daily-schedule.md](references/workflows/daily-schedule.md)

### 9. Prep for Upcoming Events
**Triggers:** "What do I need to prepare for?", "Do I have any meetings that need prep?"

Scan next 7 days for meetings needing preparation, suggest creating prep projects/tasks.

**Details:** See [references/workflows/prep-for-events.md](references/workflows/prep-for-events.md)

### 10. Process Reminders Inbox
**Triggers:** "Process my reminders", "Check Reminders inbox"

Fetch incomplete items from Reminders "Todo List", apply GTD clarification, move to Todoist/Obsidian, mark complete.

**Details:** See [references/workflows/process-reminders.md](references/workflows/process-reminders.md)

## Metadata System

### Context Labels
`@home`, `@work`, `@computer`, `@phone`, `@errands`, `@anywhere`

### Energy Labels
`#energy-high`, `#energy-medium`, `#energy-low`

### Duration
Use Todoist's native `duration` field: `5m`, `15m`, `30m`, `1h`, `2h`

### Priority
Use Todoist's native priority field: `p1` (highest), `p2` (high), `p3` (medium), `p4` (default/lowest)

### Metadata Inference

When moving items to Next Actions, infer metadata from task content:

**Context:**
- "book", "search", "email", "write" → `@computer`
- "call", "text" → `@phone`
- "buy", "pick up", "drop off" → `@errands`

**Energy:**
- Creative work, strategic thinking, coding → `#energy-high`
- Meetings, planning, research → `#energy-medium`
- Admin tasks, booking, simple lookups → `#energy-low`

**Time:**
- "Quick", "check", "look up" → `5m`
- "Call", "book", "send email" → `15m`
- "Write", "research", "plan" → `30m` to `1h`

Use AskUserQuestion to confirm inferred values.

## File Operations

**Todoist Read:**
- `mcp__todoist__find-tasks` - Search/filter tasks
- `mcp__todoist__find-projects` - List projects
- `mcp__todoist__get-overview` - Get account overview

**Todoist Write:**
- `mcp__todoist__add-tasks` - Create new tasks
- `mcp__todoist__update-tasks` - Modify existing tasks
- `mcp__todoist__complete-tasks` - Mark tasks complete
- `mcp__todoist__delete-object` - Delete tasks/projects

**Obsidian:**
- Use Read tool for project documentation in `4_Projects/`
- Use Write tool to create new project notes
- Use Edit tool to update project documentation

**Reminders (via iMCP):**
- `mcp__iMCP__reminders_lists` - List available reminder lists
- `mcp__iMCP__reminders_fetch` - Get reminders (filter by list, completed status)
- `mcp__iMCP__reminders_create` - Create new reminders

**Email (via zerolib-email MCP):**
- `mcp__zerolib-email__list_emails_metadata` - Search/filter emails
- `mcp__zerolib-email__get_emails_content` - Read full email content
- `mcp__zerolib-email__send_email` - Send emails or replies

## Conversation Style

- Be conversational but efficient
- Ask one question at a time during processing
- Provide clear options when asking for decisions
- Celebrate completions
- Be encouraging but not patronizing
- When filtering returns no matches, explain why and suggest relaxing criteria
- When referencing vault documents, use Obsidian URL scheme links (e.g., `obsidian://open?vault=obsidian-vault&file=4_Projects%2FProjectName`)

## Obsidian Integration

### URI Link Generation

**Basic format:**
```
obsidian://open?vault=obsidian-vault&file=4_Projects%2F[ProjectName]
```

**URL Encoding:**
- Forward slashes (`/`) → `%2F`
- Spaces → `%20`
- Headings (`#`) → `%23`

**Link to heading:**
```
obsidian://open?vault=obsidian-vault&file=4_Projects%2F[ProjectName]%23Next%20Actions
```

**Include in Todoist task descriptions:**
```
[Task outcome description]

Context: obsidian://open?vault=obsidian-vault&file=4_Projects%2F[ProjectName]
```

### Project Note Template

```markdown
---
tags:
  - type/project
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
status: active
todoist: https://app.todoist.com/app/task/[task-id]
---

# [Project Name]

## Desired Outcome
[What does "done" look like?]

## Context
[Background, research, decisions...]

## Next Actions
- [ ] First action @context #energy duration
- [ ] Second action @context #energy duration

**Currently in Todoist:** [active task name]

## Waiting For
- [ ] Person to do thing (requested YYYY-MM-DD)

## Notes
[Planning notes, links...]
```

## References

For detailed information, consult:

- [references/gtd-workflow.md](references/gtd-workflow.md) - Complete GTD clarification decision tree with examples
- [references/energy-time-guide.md](references/energy-time-guide.md) - Detailed guidelines for estimating energy and time requirements
- [references/backend-mapping.md](references/backend-mapping.md) - Todoist MCP tool usage patterns and examples
- [references/calendar-integration.md](references/calendar-integration.md) - Calendar MCP usage details

Load these references when:
- User asks detailed questions about the GTD process
- Uncertain how to categorize energy/time for a specific task type
- Processing complex or ambiguous inbox items
- Working with time blocking or deep work scheduling
