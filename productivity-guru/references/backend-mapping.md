# Backend Integration Mapping

This document defines the abstract operations needed by the productivity system and how they map to specific backend implementations.

## Abstract Operations

These are the core operations the productivity guru skill needs to perform:

1. **capture** - Add a new item to the inbox
2. **list_inbox** - Get all items in the inbox
3. **list_by_context** - Get items from a specific GTD list (next-actions, projects, etc.)
4. **search** - Find items by keyword or criteria
5. **add_metadata** - Add tags/metadata to an item (context, energy, time)
6. **move_to_list** - Move item between GTD lists
7. **mark_complete** - Archive or mark an item as done
8. **get_item** - Get details of a single item
9. **filter_by_metadata** - Filter items by multiple criteria (context + energy + time)

---

## Drafts App Implementation

### GTD List Structure
Use tags to represent GTD lists:
- `inbox` - Collection/capture area
- `next-actions` - Actionable single tasks
- `projects` - Multi-step outcomes
- `waiting-for` - Blocked items
- `someday-maybe` - Future possibilities
- `reference` - Information to keep

### Metadata Tags
**Context:** `@home`, `@work`, `@computer`, `@phone`, `@errands`, `@anywhere`

**Energy:** `#energy-high`, `#energy-medium`, `#energy-low`

**Time:** `#time-5m`, `#time-15m`, `#time-30m`, `#time-1h`, `#time-2h`

**Priority:** Use Drafts' built-in flagged status for high priority

### URL Scheme Mappings

#### 1. capture
**Operation:** Add new item to inbox

**URL Scheme:**
```
drafts://x-callback-url/create?text=[TEXT]&tag=inbox&action=[ACTION_NAME]
```

**Parameters:**
- `text` (required) - The task description
- `tag=inbox` (required) - Tags the draft as inbox item
- `action` (optional) - Run a Drafts action after creation

**Example:**
```
drafts://x-callback-url/create?text=pickup%20laundry&tag=inbox
```

---

#### 2. list_inbox
**Operation:** Get all items in inbox

**URL Scheme:**
```
drafts://x-callback-url/search?tag=inbox
```

**Parameters:**
- `tag=inbox` - Filter to inbox items only

**Returns:** Opens Drafts with search results

**Note:** For programmatic access, may need to use Drafts scripting or x-callback-url with a custom action

---

#### 3. list_by_context
**Operation:** Get items from specific GTD list

**URL Scheme:**
```
drafts://x-callback-url/search?tag=[GTD_LIST]
```

**Parameters:**
- `tag` - One of: `next-actions`, `projects`, `waiting-for`, `someday-maybe`, `reference`

**Examples:**
```
drafts://x-callback-url/search?tag=next-actions
drafts://x-callback-url/search?tag=projects
```

---

#### 4. search
**Operation:** Find items by keyword

**URL Scheme:**
```
drafts://x-callback-url/search?query=[KEYWORD]&tag=[TAG]
```

**Parameters:**
- `query` (optional) - Text to search for
- `tag` (optional) - Filter by tag

**Example:**
```
drafts://x-callback-url/search?query=laundry&tag=next-actions
```

---

#### 5. add_metadata
**Operation:** Add tags (context/energy/time) to an item

**URL Scheme:**
```
drafts://x-callback-url/update?uuid=[UUID]&addTags=[TAG1],[TAG2]
```

**Parameters:**
- `uuid` (required) - Draft identifier
- `addTags` (required) - Comma-separated tags to add

**Example:**
```
drafts://x-callback-url/update?uuid=ABC-123&addTags=@errands,#energy-low,#time-15m
```

---

#### 6. move_to_list
**Operation:** Move item between GTD lists

**URL Scheme:**
```
drafts://x-callback-url/update?uuid=[UUID]&removeTags=[OLD_LIST]&addTags=[NEW_LIST]
```

**Parameters:**
- `uuid` (required) - Draft identifier
- `removeTags` (required) - Remove old GTD list tag
- `addTags` (required) - Add new GTD list tag

**Example:**
```
drafts://x-callback-url/update?uuid=ABC-123&removeTags=inbox&addTags=next-actions
```

---

#### 7. mark_complete
**Operation:** Archive or mark item as done

**URL Scheme:**
```
drafts://x-callback-url/update?uuid=[UUID]&flag=true&archive=true
```

**Parameters:**
- `uuid` (required) - Draft identifier
- `flag=true` (optional) - Mark as flagged
- `archive=true` (optional) - Move to archive

**Example:**
```
drafts://x-callback-url/update?uuid=ABC-123&archive=true
```

---

#### 8. get_item
**Operation:** Get details of a single item

**URL Scheme:**
```
drafts://x-callback-url/get?uuid=[UUID]
```

**Parameters:**
- `uuid` (required) - Draft identifier

**Returns:** Draft content via x-callback-url return parameters

---

#### 9. filter_by_metadata
**Operation:** Filter items by multiple criteria

**URL Scheme:**
```
drafts://x-callback-url/search?tag=[TAG1],[TAG2],[TAG3]
```

**Parameters:**
- `tag` - Comma-separated tags (combine GTD list + context + energy + time)

**Example:**
```
drafts://x-callback-url/search?tag=next-actions,@computer,#energy-medium
```

**Note:** Drafts will AND the tags together, so this finds items that have ALL specified tags.

---

## Implementation Notes for Drafts

### Using x-callback-url for Data Return

For operations that need to return data (not just open Drafts), use x-callback-url parameters:

```
drafts://x-callback-url/[operation]?[params]&x-success=[callback_url]
```

The callback URL will receive the result data as URL parameters.

### Drafts Actions for Complex Operations

For more complex operations (like filtering and sorting), create Drafts actions that:
1. Search/filter drafts based on criteria
2. Process results
3. Return formatted data via x-callback-url

### Alternative: Drafts Scripting API

Drafts also has a JavaScript scripting API that could be used for more complex operations:
- More control over filtering and sorting
- Can process multiple drafts programmatically
- Can format output as needed

Consider creating custom Drafts actions that use scripting for:
- "What should I work on?" workflow (filter + sort + present options)
- Inbox processing (iterate through inbox items)
- Project status reports

---

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

### Filtering Limitations

Todoist MCP filtering:
- Can filter by labels with AND/OR operators
- Can filter by project
- Cannot directly filter by duration in search

For time-based filtering, fetch results and post-process by duration field.

### Data Return Format

Unlike Drafts (which opens UI), Todoist MCP returns structured data. The backend helper should:
1. Call MCP tool
2. Format results for display
3. Return structured data to skill

This enables programmatic workflows without UI interaction.

---

## Apple Reminders (iMCP) Implementation

### GTD List Structure

Use Apple Reminders lists to represent GTD contexts:
- **inbox** - Reminders list named "Inbox"
- **next-actions** - Reminders list named "Next Actions"
- **projects** - Reminders list named "Projects"
- **waiting-for** - Reminders list named "Waiting For"
- **someday-maybe** - Reminders list named "Someday/Maybe"
- **reference** - Reminders list named "Reference"

**Note:** List names must match exactly for the mapping to work correctly.

### Metadata Mapping

Since Apple Reminders doesn't support custom tags/labels natively, we encode metadata in the reminder title using a structured format:

**Title format:** `[Task description] @context #energy #time`

**Context tags:** `@home`, `@work`, `@computer`, `@phone`, `@errands`, `@anywhere`

**Energy tags:** `#energy-high`, `#energy-medium`, `#energy-low`

**Time tags:** `#time-5m`, `#time-15m`, `#time-30m`, `#time-1h`, `#time-2h`

**Priority:** Use Apple Reminders' built-in priority field
- high = High priority
- medium = Medium priority
- low = Low priority
- none = None (default)

### Direct MCP Tool Usage

The iMCP backend uses MCP tools directly. Here's how each abstract operation maps:

#### 1. capture
**Operation:** Add new item to inbox

**Direct Call:**
```
mcp__imcp__reminders_create with:
  title: "task description",
  list: "Inbox"
```

**With metadata (encoded in title):**
```
mcp__imcp__reminders_create with:
  title: "task description @computer #energy-medium #time-30m",
  list: "Inbox"
```

---

#### 2. list_inbox
**Operation:** Get all items in inbox

**Direct Call:**
```
mcp__imcp__reminders_fetch with:
  lists: ["Inbox"],
  completed: false
```

---

#### 3. list_by_context
**Operation:** Get items from specific GTD list

**Direct Call:**
```
mcp__imcp__reminders_fetch with:
  lists: ["Next Actions"],  # or "Projects", "Waiting For", "Someday/Maybe", "Reference"
  completed: false
```

**Examples:**
```
# Get all next actions
mcp__imcp__reminders_fetch with:
  lists: ["Next Actions"],
  completed: false

# Get all projects
mcp__imcp__reminders_fetch with:
  lists: ["Projects"],
  completed: false
```

---

#### 4. search
**Operation:** Find items by keyword

**Direct Call:**
```
mcp__imcp__reminders_fetch with:
  query: "search keyword",
  completed: false
```

**With GTD list filter:**
```
mcp__imcp__reminders_fetch with:
  query: "search keyword",
  lists: ["Next Actions"],
  completed: false
```

---

#### 5. add_metadata
**Operation:** Add tags/metadata to an item (context, energy, time)

**Implementation:** Since iMCP doesn't support updating existing reminders, you need to:
1. Fetch the reminder by ID or search
2. Delete the old reminder
3. Create a new reminder with updated title containing metadata

**Note:** This is a limitation of the current iMCP implementation. Future versions may support update operations.

**Workaround:**
For now, guide users to manually edit reminder titles to add metadata tags, or recreate the reminder with metadata included from the start during inbox processing.

---

#### 6. move_to_list
**Operation:** Move item between GTD lists

**Implementation:** Similar to add_metadata, this requires:
1. Fetch the reminder
2. Delete from old list
3. Create in new list with same content

**Note:** This is a limitation of the current iMCP implementation.

**Workaround:**
Guide users to manually move reminders between lists in the Reminders app, or recreate when processing.

---

#### 7. mark_complete
**Operation:** Mark item as done

**Implementation:** iMCP doesn't currently support marking reminders complete via MCP.

**Workaround:**
Guide users to manually complete reminders in the Reminders app. Future iMCP versions may support completion.

---

#### 8. get_item
**Operation:** Get details of a single item

**Direct Call:**
```
mcp__imcp__reminders_fetch with:
  query: "exact reminder title or partial match",
  completed: false,
  limit: 1
```

**Note:** Search by title text to find specific reminders.

---

#### 9. filter_by_metadata
**Operation:** Filter items by multiple criteria (context + energy + time)

**Direct Call:**
```
mcp__imcp__reminders_fetch with:
  lists: ["Next Actions"],
  query: "@computer #energy-medium",
  completed: false
```

**How it works:**
- The query parameter searches reminder titles
- Since metadata is encoded in titles, searching for tag strings filters by metadata
- For multiple tags, include all in the query string: "@computer #energy-medium #time-30m"

**Implementation notes:**
- iMCP searches titles as text, not structured tags
- Use query with tag strings: `"@computer #energy-medium"` will find reminders with both in title
- Post-process results if needed to ensure all criteria match

**Example:**
```
# Find next actions for computer with medium energy
mcp__imcp__reminders_fetch with:
  lists: ["Next Actions"],
  query: "@computer #energy-medium",
  completed: false
```

---

## Implementation Notes for iMCP

### Initial Setup Required

Before using iMCP backend, create these reminder lists in Apple Reminders:
1. Inbox
2. Next Actions
3. Projects
4. Waiting For
5. Someday/Maybe
6. Reference

**To verify lists exist:**
```
mcp__imcp__reminders_lists
```

### Metadata Encoding Strategy

Since Apple Reminders doesn't have native tag support, we embed metadata in the title:

**Format:** `[Description] @context #energy #time`

**Examples:**
- `Buy groceries @errands #energy-low #time-30m`
- `Write blog post @computer #energy-high #time-2h`
- `Call dentist @phone #energy-low #time-15m`

**Parsing rules:**
- Context always starts with `@`
- Energy always starts with `#energy-`
- Time always starts with `#time-`
- Tags can appear in any order at end of title
- Multiple spaces between tags are ok

### Current Limitations

The iMCP implementation has several limitations compared to Todoist/Drafts:

1. **No update support** - Can't modify existing reminders via MCP
2. **No completion support** - Can't mark reminders complete via MCP
3. **No move support** - Can't move reminders between lists via MCP
4. **Title-based metadata** - Must encode tags in title text, not native fields
5. **Text search only** - Query searches title text, not structured metadata

**Workarounds:**
- For update/move/complete operations, guide users to use Reminders app manually
- For metadata, use consistent title format and text search
- Consider Todoist or Drafts backends if programmatic updates are critical

### When to Use iMCP Backend

**Good fit when:**
- User already uses Apple Reminders
- Read-only operations are sufficient (listing, filtering, searching)
- Quick capture is primary use case
- User is willing to manually process/update in Reminders app
- Apple ecosystem integration is important

**Not ideal when:**
- Need programmatic updates, moves, or completions
- Heavy automation is required
- Cross-platform access needed
- Prefer text search over structured metadata

### Filtering Performance

Since iMCP uses title text search for metadata filtering:
- Simple queries (1-2 tags) work well
- Complex queries (3+ tags) may need post-processing
- False positives possible if tags appear in description
- Consider post-filtering results in skill code for exact matches

**Best practice:**
Keep metadata tags at end of title to minimize false matches.

---

## Future Backend Options

This mapping can be extended to other backends:

### Plain Text Files
- **capture** → Append to `inbox.txt`
- **list_inbox** → Read `inbox.txt`
- **move_to_list** → Move line from one file to another
- etc.

---

## Design Principles

1. **Backend Agnostic** - The skill should work with the abstract operations, not implementation details
2. **Swappable** - Should be able to change backends with minimal skill changes
3. **Feature Parity** - All backends should support the same core operations
4. **Graceful Degradation** - If a backend doesn't support an operation, fail gracefully

## Usage in SKILL.md

The main SKILL.md should reference this mapping and say:
- "Use the `capture` operation to add items to inbox"
- NOT "Use `drafts://x-callback-url/create?...`"

Include specific implementation details in a separate "Drafts Backend" section or reference this document.
