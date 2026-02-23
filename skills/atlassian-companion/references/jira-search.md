# Jira Search and JQL Patterns

## jira_search

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `jql` | Yes | string | JQL query string |
| `fields` | No | string | Comma-separated fields to return |
| `limit` | No | integer | 1-50, default 10 |
| `start_at` | No | integer | Pagination offset, 0-based |
| `projects_filter` | No | string | Comma-separated project keys |
| `expand` | No | string | `renderedFields`, `transitions`, `changelog` |

## JQL Patterns That Work

### By status
```jql
project = <PROJECT> AND status = "In Progress"
project = <PROJECT> AND status != Done
project = <PROJECT> AND status not in (Done, Closed)
```

### By assignee
```jql
assignee = currentUser()
assignee = "user@example.com"
```

### By label
```jql
project = <PROJECT> AND labels = "v2-wrapper"
```

### By date
```jql
updated >= -7d AND project = <PROJECT>
created >= "2026-01-01" AND project = <PROJECT>
```

### By issue type
```jql
project = <PROJECT> AND issuetype = Bug
project = <PROJECT> AND issuetype in (Bug, Task)
```

### By Epic / parent
```jql
parent = <PROJECT>-100
"Epic Link" = <PROJECT>-100
```

### Combined with ordering
```jql
project = <PROJECT> AND status != Done ORDER BY priority DESC, updated DESC
```

## JQL Patterns That FAIL Silently

### Numeric comparisons on Story Points
These operators do NOT work on "Story point estimate":
- `"Story point estimate" >= 5` — returns nothing
- `"Story point estimate" > 3` — returns nothing
- `"Story point estimate" < 8` — returns nothing

### Workaround
Fetch all issues with story points and filter client-side:
```jql
project = <PROJECT> AND "Story point estimate" is not EMPTY ORDER BY "Story point estimate" DESC
```

### Sprint filtering via JQL
Sprint JQL can be unreliable. Prefer using dedicated tools:
- `jira_get_sprints_from_board` to list sprints
- `jira_get_sprint_issues` to get issues in a sprint

---

## jira_search_fields

Finds Jira field definitions by keyword (fuzzy match). Useful for discovering custom field IDs.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `keyword` | No | string | Fuzzy search term. Empty = list first N fields |
| `limit` | No | integer | Default 10 |
| `refresh` | No | boolean | Force refresh field cache |

### Example: Find the Story Points field
```
keyword: "story point"
```

---

## jira_get_project_issues

Shortcut to get all issues for a project without writing JQL.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `project_key` | Yes | string | e.g., `"<PROJECT>"` |
| `limit` | No | integer | 1-50, default 10 |
| `start_at` | No | integer | Pagination offset |
