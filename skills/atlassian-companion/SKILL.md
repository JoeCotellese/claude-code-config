---
name: atlassian-companion
description: "Companion skill for the mcp-atlassian MCP server. Provides correct parameter patterns, JQL quirks, and workflow recipes for Jira and Confluence tools. Load this skill before performing Atlassian operations to avoid common parameter errors."
effort: low
---

# Atlassian MCP Companion

Reference guide for using `mcp-atlassian` MCP tools correctly. Load the relevant reference before calling Atlassian tools to avoid parameter errors and silent failures.

## When to Use

- Before creating, updating, or searching Jira issues
- Before creating or updating Confluence pages
- When JQL queries return unexpected results
- When an Atlassian MCP tool call fails with validation errors

## Quick Reference: Common Pitfalls

These are the most frequent errors. For full details, load from `references/`.

### jira_create_issue
- Use `project_key`, NOT `project`
- `priority` is NOT a top-level parameter (defaults to Medium)
- Set priority via `jira_update_issue` after creation

### jira_update_issue
- `fields` must be a JSON **object**, not a string
- `assignee`, `priority`, `labels` go INSIDE `fields`
- Assignee is a string (email), not an object

### jira_search (JQL)
- Numeric comparisons on Story Points FAIL SILENTLY
- Use `is not EMPTY` with `ORDER BY` instead of `>=`, `>`, `<`, `<=`

## Process

### Step 0: Resolve Project Context

Before any Jira operation, determine the Jira project key for the current working directory. Do NOT hardcode a project key — look it up:

1. Search the local project's `CLAUDE.md` files (both repo-level and `.claude/CLAUDE.md`) for a Jira project declaration (e.g., `project to reference is WPD`, `project_key: XYZ`, or similar)
2. Check for a `## Jira Integration` section which may also declare labeling rules per repo
3. If no project key is found, ask the user

Use the discovered project key in all `project_key` parameters and JQL queries. If the project's CLAUDE.md also specifies **labels by repo** (e.g., `react-native-wavelydx-v2` → `v2-wrapper`), apply those labels when creating issues.

### Step 1: Identify the Operation

Determine which category of Atlassian operation is needed:

| Category | Reference |
|----------|-----------|
| Jira CRUD (create/read/update/delete) | `references/jira-crud.md` |
| Jira search and JQL patterns | `references/jira-search.md` |
| Jira workflow (sprints, transitions, links) | `references/jira-workflow.md` |
| Confluence operations | `references/confluence.md` |

### Step 2: Load the Reference

Read the appropriate reference file for correct parameter patterns.

### Step 3: Execute with Correct Parameters

Use the patterns from the reference. If a call fails, check the reference before retrying — most failures are parameter shape issues, not API errors.
