# Jira Search and JQL with acli

## acli jira workitem search

```bash
acli jira workitem search --jql "project = PROJ AND status != Done"
acli jira workitem search --jql "project = PROJ" --fields "key,summary,assignee" --csv
acli jira workitem search --jql "project = PROJ" --limit 50 --json
acli jira workitem search --jql "project = PROJ" --count
acli jira workitem search --jql "project = PROJ" --paginate
```

Flags:

- `-j, --jql`: the query
- `--filter`: search by saved filter ID instead of JQL
- `-f, --fields`: comma-separated. Default is
  `issuetype,key,assignee,priority,status,summary`
- `-l, --limit`: maximum items to fetch
- `--paginate`: fetch everything, ignoring `--limit`
- `--count`: return only the number of matches
- `--json` / `--csv`: machine-readable output
- `-w, --web`: open the search in a browser

`--count` is the cheap way to size a result set. Use it before any `--jql` write, and use it
instead of fetching everything when the user only asked "how many".

Quote the whole JQL string in the shell. Values containing spaces need inner quotes, so use
double quotes outside and single quotes inside:

```bash
acli jira workitem search --jql "project = PROJ AND status = 'In Progress'"
```

## JQL Patterns That Work

These are properties of Jira's JQL, not of `acli`, so they carry over unchanged.

By status:

```
project = PROJ AND status = "In Progress"
project = PROJ AND status != Done
project = PROJ AND status not in (Done, Closed)
```

By assignee:

```
assignee = currentUser()
assignee = "user@example.com"
```

By label:

```
project = PROJ AND labels = "v2-wrapper"
```

By date:

```
updated >= -7d AND project = PROJ
created >= "2026-01-01" AND project = PROJ
```

By work item type:

```
project = PROJ AND issuetype = Bug
project = PROJ AND issuetype in (Bug, Task)
```

By Epic or parent:

```
parent = PROJ-100
"Epic Link" = PROJ-100
```

With ordering:

```
project = PROJ AND status != Done ORDER BY priority DESC, updated DESC
```

## JQL Patterns That FAIL Silently

### Numeric comparisons on Story Points

These operators return nothing rather than erroring on "Story point estimate":

- `"Story point estimate" >= 5`
- `"Story point estimate" > 3`
- `"Story point estimate" < 8`

An empty result looks identical to "no matching items", so the failure is invisible.

Workaround: select the non-empty set, order by the field, and filter in the shell:

```bash
acli jira workitem search \
  --jql "project = PROJ AND 'Story point estimate' is not EMPTY ORDER BY 'Story point estimate' DESC" \
  --json | jq '...'
```

### Sprint filtering

Sprint predicates in JQL are unreliable. Prefer the dedicated commands:

```bash
acli jira board list-sprints --id 123 --state active
acli jira sprint list-workitems --sprint 45 --board 123
```

`sprint list-workitems` also accepts `--jql` to filter within the sprint, which is more reliable
than putting the sprint itself in the query.

## Getting all work items for a project

There is no project-issues shortcut. Use search:

```bash
acli jira workitem search --jql "project = PROJ" --paginate
```
