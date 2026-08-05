# Jira Work Item CRUD with acli

All commands are `acli jira workitem <verb>`. Add `--json` to any of them for machine-readable
output.

## create

Creates one work item.

```bash
acli jira workitem create \
  --project "PROJ" \
  --type "Bug" \
  --summary "Login times out on slow networks" \
  --assignee "user@example.com" \
  --label "frontend,v2-wrapper"
```

Flags:

- `-p, --project` (required in practice): project key, e.g. `PROJ`
- `-t, --type` (required): work item type, **case sensitive**: `Epic`, `Story`, `Task`, `Bug`
- `-s, --summary`: the title
- `-d, --description`: plain text or ADF. See "Descriptions" below
- `--description-file`: read the description from a file, plain text or ADF
- `-a, --assignee`: email or account ID. `@me` self-assigns; `default` uses the project default
- `-l, --label`: comma-separated label names
- `--parent`: parent work item ID
- `-f, --from-file`: read summary and description from a file
- `--from-json`: read the whole definition from a JSON file
- `--generate-json`: print a JSON template to stdout, then fill it in
- `-e, --editor`: opens an interactive editor. **Never use this.** It blocks on a TTY

There is no `--priority` flag. Priority must go through `additionalAttributes` in the JSON path,
which is unverified. Ask the user rather than guessing.

`--parent` is documented in the JSON template as "only if the work item is a sub-task". Whether
it also links a Story to an Epic is unverified. Check the result after the first use.

## Descriptions

`acli` does no markdown conversion. A description is either a plain string or Atlassian Document
Format JSON. Markdown written into `--description` arrives as literal text: `## Steps` shows up
as `## Steps`, and `1. item` stays a line beginning with `1.` rather than becoming a list.

For a one-line description, plain text is fine:

```bash
acli jira workitem create --project PROJ --type Task \
  --summary "Bump the retry ceiling" \
  --description "Raise the network retry ceiling from 15s to 30s."
```

For structured content, write ADF to a file and pass `--description-file`. The minimal envelope:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 3 },
      "content": [{ "type": "text", "text": "Problem" }]
    },
    {
      "type": "paragraph",
      "content": [{ "type": "text", "text": "Login times out after 15s on 3G." }]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{ "type": "text", "text": "Timeout extended to 30s" }]
            }
          ]
        }
      ]
    }
  ]
}
```

Useful ADF node types: `paragraph`, `heading` (with `attrs.level`), `bulletList` and
`orderedList` (each child is a `listItem` wrapping a `paragraph`), `codeBlock` (with
`attrs.language`), `rule`. Inline emphasis goes on a text node as
`"marks": [{"type": "strong"}]`, with `em`, `code`, and `strike` as the other common marks.

Because ADF carries formatting in structure rather than in punctuation, there are no escaping
rules to remember. Angle brackets, underscores, and `++` survive literally inside a text node.
Put code in a `codeBlock` and it stays intact.

Write the ADF file to the scratchpad directory, not into the user's repo.

## The JSON path

`--generate-json` prints a template you can fill in and pass back through `--from-json`:

```bash
acli jira workitem create --generate-json > /path/to/scratchpad/workitem.json
# edit it
acli jira workitem create --from-json /path/to/scratchpad/workitem.json
```

The create template's keys are `projectKey`, `type`, `summary`, `description` (ADF object),
`assignee`, `reporter`, `labels` (array), `parentIssueId`, and `additionalAttributes` (an object
keyed by custom field ID, e.g. `customfield_10001`).

Note the key names differ from the flags: `projectKey` not `project`, `labels` not `label`.

## view

```bash
acli jira workitem view PROJ-123
acli jira workitem view PROJ-123 --fields summary,comment
acli jira workitem view PROJ-123 --json
```

The key is a positional argument, not a flag. Default fields are
`key,issuetype,summary,status,assignee,description`, so comments, labels, and priority are
absent unless requested.

`--fields` accepts `*all`, `*navigable`, and minus-prefixed exclusions such as
`*navigable,-comment`.

`-w, --web` opens it in a browser. Only use it when the user asks to see the item.

## edit

```bash
acli jira workitem edit --key "PROJ-123" --summary "New summary"
acli jira workitem edit --key "PROJ-123,PROJ-124" --assignee "user@example.com" --yes
```

Flags:

- `-k, --key`: comma-separated work item keys
- `--jql` / `--filter`: select items to edit in bulk. See the guardrail below
- `-s, --summary`, `-d, --description`, `--description-file`, `-t, --type`
- `-a, --assignee`, `--remove-assignee`
- `-l, --labels`, `--remove-labels`
- `-y, --yes`: skip the confirmation prompt
- `--ignore-errors`: continue past failures in a multi-item edit
- `--from-json` / `--generate-json`

Whether `--labels` replaces the existing set or adds to it is unverified. The JSON path is
unambiguous and is the safer choice when it matters: the edit template exposes `labelsToAdd` and
`labelsToRemove` as separate arrays, so additive edits are explicit.

The edit JSON template's keys are `issues` (array of keys), `summary`, `description` (ADF),
`type`, `assignee`, `labelsToAdd`, `labelsToRemove`.

### Bulk guardrail

`--jql` and `--filter` on `edit` apply to every matching work item. Before running one:

```bash
acli jira workitem search --jql "project = PROJ AND status = 'To Do'" --count
```

Report the count to the user and get approval before adding `--yes`.

## delete

```bash
acli jira workitem delete --key "PROJ-123"
```

Irreversible. Always confirm with the user first, and never combine `--jql` with `--yes` on a
delete. Same flags as `edit` for selection: `--key`, `--jql`, `--filter`, `--from-file`.

## comment

```bash
acli jira workitem comment create --key "PROJ-123" --body "Fixed in v2.1.0."
acli jira workitem comment create --key "PROJ-123" --body-file /path/to/comment.json
acli jira workitem comment list --key "PROJ-123"
```

- `create`: `-b, --body` (plain text or ADF), `-F, --body-file`, `-e, --edit-last` to amend your
  own last comment, `--editor` (never use, it blocks on a TTY)
- `list`: `--key`, `--limit` (default 50), `--order` (`created` or `updated`, prefix with `-` to
  reverse), `--paginate`
- `update`, `delete`, `visibility` also exist

Comment bodies follow the same plain-text-or-ADF rule as descriptions.

## assign

```bash
acli jira workitem assign --key "PROJ-123" --assignee "@me"
```

`--assignee` takes an email, an account ID, `@me`, or `default`. `--remove-assignee` clears it.

## clone

```bash
acli jira workitem clone --key "PROJ-123" --to-project "TEAM"
```

`--to-site` targets a different Atlassian site; it defaults to the authenticated one.

## attachment

Only `list` and `delete`. `acli` cannot upload an attachment.

```bash
acli jira workitem attachment list --key "PROJ-123"
```

## Not available in acli

These have no `acli` equivalent. If a task needs one, tell the user rather than working around
it:

- Uploading attachments
- Worklogs and time tracking
- Project versions and releases
- Remote links to external URLs, such as a GitHub PR
- Searching field definitions by keyword (`acli jira field` only creates, updates, and deletes
  custom fields; it cannot list them)
