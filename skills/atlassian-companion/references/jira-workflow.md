# Jira Workflow Operations with acli

## Transitions (Status Changes)

```bash
acli jira workitem transition --key "PROJ-123" --status "Done"
acli jira workitem transition --key "PROJ-123,PROJ-124" --status "In Progress" --yes
```

Flags: `-k, --key`, `--jql`, `--filter`, `-s, --status`, `-y, --yes`, `--ignore-errors`,
`--json`.

`--status` takes the target status **by name**. There is no transition ID and no command that
lists the transitions available from the current status, so an invalid or unreachable status
name only surfaces as a command failure.

Before transitioning an item whose workflow you do not know:

```bash
acli jira workitem view PROJ-123 --fields status
```

Status names are workflow-specific. `Done` on one project may be `Closed` or `Resolved` on
another. If a transition fails, read the error rather than trying names at random, and ask the
user for the correct one after one failed guess.

`--jql` transitions in bulk. Size it with `search --count` first, and get approval before adding
`--yes`.

## Links Between Work Items

List the link types your instance actually has:

```bash
acli jira workitem link type
```

Create a link:

```bash
acli jira workitem link create --out PROJ-123 --in PROJ-456 --type Blocks
```

Direction matters. `--out` is the outward item and `--in` the inward one, so the example above
reads "PROJ-123 blocks PROJ-456". `--type` accepts the outward description of the link type,
which is why `link type` is worth running when you are unsure.

Multiple links at once:

```bash
acli jira workitem link create --generate-json > /path/to/scratchpad/links.json
acli jira workitem link create --from-json /path/to/scratchpad/links.json
```

The template is an array of objects with `inwardIssue`, `outwardIssue`, and `type`. A CSV path
exists too via `--from-csv`, with columns outward, inward, type, and the first row ignored as a
header.

List and remove:

```bash
acli jira workitem link list --key PROJ-123
acli jira workitem link delete --help
```

### Epic links

There is no `link-to-epic` command. `create --parent <id>` is the closest thing, and the JSON
template describes `parentIssueId` as being for sub-tasks. Whether it also attaches a Story to
an Epic is unverified. Test it on one work item and check the result in Jira before doing it in
bulk.

### Remote links

`acli` cannot create a remote link to an external URL such as a GitHub PR. Put the URL in a
comment instead, or tell the user this needs the web UI.

## Sprints

```bash
acli jira sprint create --name "Sprint 12" --board 5 --start 2026-08-10 --end 2026-08-24
acli jira sprint create --name "Release Planning" --board 10 --goal "Prepare for Q3 release"
acli jira sprint view --help
acli jira sprint update --help
acli jira sprint delete --help
```

`create` requires `--name` and `--board`. Dates are ISO 8601, either `2026-08-10` or
`2026-08-10T09:00:00Z`. `--goal` sets the sprint goal.

List work items in a sprint (both flags required):

```bash
acli jira sprint list-workitems --sprint 45 --board 5
acli jira sprint list-workitems --sprint 45 --board 5 --jql "assignee = currentUser()"
```

Also accepts `--fields`, `--limit` (default 50), `--paginate`, `--json`, `--csv`.

There is no command that moves a work item into or out of a sprint. That needs the web UI.

## Boards

```bash
acli jira board search
acli jira board view --help
acli jira board list-sprints --id 123 --state active,closed
acli jira board list-projects --help
```

`board search` finds boards and their IDs, which the sprint commands need. `list-sprints`
accepts `--state` with `future`, `active`, `closed`, comma-separated, plus `--limit`,
`--paginate`, `--json`, `--csv`.

Note the asymmetry: `board get` and `filter get` are marked DEPRECATED in the CLI's own help.
Use `view` instead of `get` for both.

There is no command that lists all work items on a board. Use `workitem search` with a JQL query
or `sprint list-workitems`.

## Projects

```bash
acli jira project list --recent
acli jira project list --paginate --json
acli jira project view --help
```

`list` defaults to a limit of 30. `--recent` returns up to 20 recently viewed projects, which is
usually what you want when resolving an ambiguous project key with the user.

`create`, `update`, `archive`, `restore`, and `delete` also exist. Treat all five as
user-approval operations.

## Filters

```bash
acli jira filter list
acli jira filter search --help
acli jira filter view --help
```

A filter ID from these commands can be passed as `--filter` to `workitem search`, `edit`,
`transition`, `delete`, `assign`, and `clone`. The same bulk guardrail applies: a filter can
match hundreds of items.

## Bulk Creation

```bash
acli jira workitem create-bulk --generate-json > /path/to/scratchpad/issues.json
acli jira workitem create-bulk --from-json /path/to/scratchpad/issues.json
```

The template is an object with an `issues` array, each entry having `summary`, `projectKey`,
`issueType`, `label` (array), `assignee`, and optionally `description` and `parentIssueId`.

Note the key names differ from the single-create template: `issueType` here versus `type` there,
`label` here versus `labels` there. Generate the template rather than writing it from memory.

`--from-csv` takes columns `summary, projectKey, issueType, description, label, parentIssueId,
assignee`.

`--ignore-errors` continues past a failed row. Without it, a bad row stops the run partway,
leaving some items created and some not. Prefer running without it so a failure is loud, then
fix the input and rerun only the remainder.

Show the user the JSON before running `create-bulk`. It is the fastest way in this toolset to
create fifty wrong tickets.

## Archive

```bash
acli jira workitem archive --help
acli jira workitem unarchive --help
```

Archiving is reversible, unlike delete. When a user asks to "get rid of" work items, offer
archive first.
