# Jira CRUD Operations

## jira_create_issue

Creates a new Jira issue. Returns the created issue with key and URL.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `project_key` | Yes | string | e.g., `"PROJ"`. Do NOT use `project` |
| `summary` | Yes | string | Issue title |
| `issue_type` | Yes | string | `"Bug"`, `"Task"`, `"Story"`, `"Epic"` |
| `description` | No | string | Jira wiki markup (use `*bold*`, `_italic_`, `{{code}}`, `* bullets`) |

### What You CANNOT Set at Creation
- `priority` — defaults to Medium, update after creation
- `labels` — update after creation
- `assignee` — update after creation
- `story_points` — update after creation

### Example
```
project_key: "<PROJECT_KEY>"       # Resolve from local CLAUDE.md (Step 0)
summary: "Fix login timeout on slow networks"
issue_type: "Bug"
description: "*Problem*\nLogin times out after 15s on 3G.\n\n*Acceptance Criteria*\n* Timeout extended to 30s\n* Retry logic added"
```

### Post-Creation Pattern
Create first, then immediately update with fields that aren't supported at creation:
```
# Step 1: Create
jira_create_issue(project_key="<PROJECT_KEY>", summary="...", issue_type="Task")

# Step 2: Update with priority, labels, assignee
jira_update_issue(issue_key="<PROJECT_KEY>-123", fields={"priority": {"name": "High"}, "labels": ["<repo-label>"], "assignee": "user@example.com"})
```

---

## jira_get_issue

Retrieves a single issue by key.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | e.g., `"PROJ-123"` |
| `fields` | No | string | Comma-separated. Default: `summary,issuetype,status,priority,description,updated,assignee,labels,reporter,created`. Use `*all` for everything |
| `expand` | No | string | `renderedFields`, `transitions`, `changelog` |
| `comment_limit` | No | integer | 0-100, default 10. Set to 0 for no comments |

---

## jira_update_issue

Updates an existing issue. The `fields` parameter is where most mistakes happen.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | e.g., `"PROJ-123"` |
| `fields` | Yes | **object** | Must be a dict/object, NOT a JSON string |
| `additional_fields` | No | object | For custom fields or complex updates |
| `attachments` | No | string | Comma-separated file paths |

### Fields Object Patterns

**Assignee** — pass email as a plain string:
```json
{"assignee": "user@example.com"}
```

**Priority** — pass as an object with `name`:
```json
{"priority": {"name": "High"}}
```

**Labels** — pass as an array of strings (replaces all labels):
```json
{"labels": ["v2-wrapper", "audio-bug"]}
```

**Summary**:
```json
{"summary": "Updated title"}
```

**Combined example**:
```json
{
  "assignee": "user@example.com",
  "priority": {"name": "High"},
  "labels": ["v2-wrapper"],
  "summary": "Updated title"
}
```

---

## jira_delete_issue

Deletes an issue permanently.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | e.g., `"PROJ-123"` |

**Warning**: This is irreversible. Always confirm with the user before deleting.

---

## jira_add_comment

Adds a comment to an issue.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | e.g., `"PROJ-123"` |
| `comment` | Yes | string | The comment text. NOT `body` |

---

## jira_edit_comment

Edits an existing comment.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `issue_key` | Yes | string | |
| `comment_id` | Yes | string | |
| `comment` | Yes | string | Updated text |
