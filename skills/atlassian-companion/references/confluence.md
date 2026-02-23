# Confluence Operations

## Reading Content

### confluence_search
Search Confluence content by text or CQL.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `query` | Yes | string | Search text or CQL query |
| `limit` | No | integer | Max results |

### confluence_get_page
Get a specific page by ID.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | Confluence page ID |

### confluence_get_page_children
Get child pages of a parent page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | Parent page ID |

### confluence_get_comments
Get comments on a page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |

### confluence_get_labels
Get labels on a page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |

---

## Writing Content

### confluence_create_page
Create a new Confluence page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `space_key` | Yes | string | Space to create in |
| `title` | Yes | string | Page title |
| `body` | Yes | string | Page content (Confluence storage format / HTML) |
| `parent_id` | No | string | Parent page ID for nesting |

### confluence_update_page
Update an existing page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |
| `title` | Yes | string | |
| `body` | Yes | string | |

### confluence_delete_page
Delete a page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |

**Warning**: Irreversible. Confirm with user before deleting.

### confluence_add_comment
Add a comment to a page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |
| `body` | Yes | string | Comment content |

### confluence_add_label
Add a label to a page.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `page_id` | Yes | string | |
| `label` | Yes | string | Label name |

---

## User Search

### confluence_search_user
Search for Confluence users.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `query` | Yes | string | Name or email to search |
