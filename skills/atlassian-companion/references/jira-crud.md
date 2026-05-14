# Jira CRUD Operations

## jira_create_issue

Creates a new Jira issue. Returns the created issue with key and URL.

### Parameters
| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `project_key` | Yes | string | e.g., `"PROJ"`. Do NOT use `project` |
| `summary` | Yes | string | Issue title |
| `issue_type` | Yes | string | `"Bug"`, `"Task"`, `"Story"`, `"Epic"` |
| `description` | No | string | **Markdown**, not raw Jira wiki markup. The MCP layer converts markdown → wiki on the way in. See "Description Formatting" below. |
| `additional_fields` | No | dict | Optional dict for `priority`, `labels`, custom fields, etc. See below. |

### Setting priority, labels, assignee at Creation
These CAN be set at creation via `additional_fields`. You do NOT need a follow-up update call.

```
additional_fields: {
  "priority": {"name": "Medium"},
  "labels": ["v2-wrapper", "frontend"]
}
```

`assignee` accepts a string identifier (email, display name, or accountId) as a top-level parameter on `jira_create_issue`.

### Description Formatting (CRITICAL)

The MCP layer interprets the `description` string as **markdown** and converts it to Jira wiki markup before sending to the API. Use markdown syntax, not raw wiki markup.

| You write (markdown) | Stored as (wiki) | Renders as |
|---|---|---|
| `1. item`<br/>`2. item` | `# item`<br/>`# item` | ✅ Numbered list |
| `* item`<br/>`* item` | `* item`<br/>`* item` | ✅ Bullet list |
| `**bold**` | `*bold*` | ✅ Bold |
| `# Heading` | `h1. Heading` | h1 heading |
| `## Subheading` | `h2. Subheading` | h2 heading |
| `### Section` | `h3. Section` | h3 heading |
| `` `code` `` | `{{code}}` | ✅ Inline code |

**⚠️ The trap:** If you write `# Open the screen` thinking it's a Jira wiki ordered list (which it would be in the web UI), the MCP will treat it as a markdown h1 and store it as `h1. Open the screen`. Always use `1.` for numbered lists when going through the MCP.

**Headings** (`h3. *Steps to Reproduce:*`) appear to pass through verbatim if you write them in raw wiki markup — but for consistency, prefer markdown `### Steps to Reproduce` and let the MCP convert.

**⚠️ Angle brackets in code blocks get stripped.** When posting TypeScript generics or JSX inside a fenced code block, the MCP layer strips `<` and `>`. Example: a `\`\`\`ts` block containing `Array<{ id: number }>` arrives in Jira as `Array[{ id: number }]`. Workarounds:
- Replace generics with prose comments: `Array /* of */ { id: number } /* */`
- Describe the type signature in prose instead of a code block
- Or accept the cosmetic loss for one-off comments — confirmed harmless to the rest of the wiki conversion

This affects both `description` on `jira_create_issue` and `comment` on `jira_add_comment`, since both flow through the same markdown→wiki layer.

### ⚠️ Code-identifier hazards in prose (the underscore/star trap)

Identifiers written as **bare prose** (no backticks) get mangled by the markdown→wiki layer because markdown reserves `_` and `*` for emphasis. The MCP escapes them on the way to wiki, producing ugly `\_` and `\*` sequences in the rendered output.

| You write (bare) | What happens | Renders as |
|---|---|---|
| `audio_files` | `_files` parsed as italic span | `audio\_files` (visible backslash) |
| `complex_short_chirp` | underscores escaped or italicized | `complex\*short\*chirp` |
| `*` between words (e.g. "6 * 3 modes") | parsed as bold/italic | escaped or eats surrounding text |
| `i++` in prose or fenced block | second `+` consumed somewhere in the pipeline | renders as `i+` |

**Fix (partial):** wrap code identifiers in backticks for inline code. This helps visual styling in some renderers, but **the MCP currently escapes `_` and `+` chars BEFORE backtick scoping is applied**, so even `` `audio_files` `` arrives in Jira as `audio\_files` with a visible backslash. Backticks are NOT a reliable shield.

**Practical workarounds (in order of preference):**
1. Rephrase to avoid the hazardous identifier: "the audio files array" instead of `audio_files`. Lose precision; gain readability.
2. Replace `_` with hyphens or camelCase when the audience will tolerate it: `audioFiles`.
3. For pseudocode, prefer `i = i + 1` over `i++` (the `+` characters survive in arithmetic context most of the time, but not always — verify in a low-stakes ticket first).
4. Accept the cosmetic backslashes. They are ugly but readable. Substance survives.
5. If correctness matters more than cosmetics (e.g., for an auditor), put the exact code in the repo and **link** from the Jira comment instead of inlining.

**Fenced code blocks (`\`\`\``) are NOT a safe haven.** Some characters (`++`, `<`, `>`, occasional `_`) still get processed even inside triple-backtick fences depending on the MCP version. For critical pseudocode, prefer:
- Rephrase to avoid hazardous characters (`for (let i = 1; i <= n; i = i + 1)` instead of `i++`)
- Use the wiki `{noformat}` block sent **without** surrounding markdown formatting — but be aware the markdown layer may still pre-process it
- Accept that pseudocode in Jira comments may render imperfectly; put exact code in the repo, link from the comment

**Rule of thumb:** if it would compile, wrap it in backticks. Treat bare prose as prose only.

### Example
```
project_key: "<PROJECT_KEY>"       # Resolve from local CLAUDE.md (Step 0)
summary: "Fix login timeout on slow networks"
issue_type: "Bug"
description: "### Problem\nLogin times out after 15s on 3G.\n\n### Steps to Reproduce\n1. Open login screen\n2. Connect to throttled network\n3. Tap Sign In\n\n### Acceptance Criteria\n* Timeout extended to 30s\n* Retry logic added"
additional_fields: {"priority": {"name": "High"}, "labels": ["frontend"]}
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

**Labels** — pass as an array of strings (replaces all labels, does NOT append):
```json
{"labels": ["v2-wrapper", "audio-bug"]}
```

⚠️ **The `fields` parameter must be a real object, not a JSON string.** If the tool call fails with:
```
1 validation error for call[update_issue]
fields
  Input should be a valid dictionary [type=dict_type, input_value='{"labels": ["wont-do"]}', input_type=str]
```
…it means the value was serialized as a string. The fix is to pass the value as a structured JSON object in the tool call, not as a quoted string. When in doubt, retry the call exactly as written — sometimes the issue is encoder-side, not your input.

⚠️ **Labels REPLACE, they don't append.** If you want to add a label without losing existing ones, first `jira_get_issue` with `fields: "labels"`, then send the merged list back.

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
