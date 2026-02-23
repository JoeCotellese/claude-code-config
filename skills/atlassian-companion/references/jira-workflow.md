# Jira Workflow Operations

## Issue Transitions (Status Changes)

### jira_get_transitions
Get available status transitions for an issue. Always call this before transitioning.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | e.g., `"PROJ-123"` |

### jira_transition_issue
Move an issue to a new status.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | |
| `transition_id` | Yes | string | From `jira_get_transitions` |

**Pattern**: Always get transitions first, then transition:
```
# Step 1: Get available transitions
jira_get_transitions(issue_key="PROJ-123")

# Step 2: Use the transition ID from results
jira_transition_issue(issue_key="PROJ-123", transition_id="31")
```

---

## Issue Links

### jira_get_link_types
Lists all available link types (Blocks, Relates to, Duplicate, etc.).

### jira_create_issue_link
Creates a link between two issues.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `link_type` | Yes | string | e.g., `"Blocks"`, `"Relates"`, `"Duplicate"` |
| `inward_issue_key` | Yes | string | The issue that IS blocked / IS related / IS duplicate |
| `outward_issue_key` | Yes | string | The issue that blocks / relates to / duplicates |

**Directionality matters**:
- `Blocks`: outward "blocks" inward → `inward=PROJ-200, outward=PROJ-100` means "PROJ-100 blocks PROJ-200"
- Call `jira_get_link_types` if unsure about available link types

### jira_remove_issue_link
Removes a link between two issues.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `link_id` | Yes | string | The link ID (from issue details) |

### jira_link_to_epic
Links an issue to an Epic.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | The child issue |
| `epic_key` | Yes | string | The Epic to link to |

### jira_create_remote_issue_link
Creates a link to an external URL (GitHub PR, doc, etc.).

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | |
| `url` | Yes | string | External URL |
| `title` | Yes | string | Link display text |

---

## Sprints and Boards

### jira_get_agile_boards
List all agile boards.

### jira_get_sprints_from_board
Get sprints for a board. Prefer this over JQL sprint filtering.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `board_id` | Yes | integer | From `jira_get_agile_boards` |

### jira_get_sprint_issues
Get issues in a specific sprint.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `sprint_id` | Yes | integer | From `jira_get_sprints_from_board` |

### jira_get_board_issues
Get all issues on a board.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `board_id` | Yes | integer | |

### jira_create_sprint / jira_update_sprint
Create or modify sprints on a board.

---

## Versions

### jira_get_project_versions
List all versions/releases for a project.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `project_key` | Yes | string | e.g., `"PROJ"` |

### jira_create_version / jira_batch_create_versions
Create release versions for a project.

---

## Worklogs

### jira_get_worklog
Get time tracking entries for an issue.

### jira_add_worklog
Add time tracking to an issue.

---

## Batch Operations

### jira_batch_create_issues
Create multiple issues at once.

### jira_batch_get_changelogs
Get change history for multiple issues.
