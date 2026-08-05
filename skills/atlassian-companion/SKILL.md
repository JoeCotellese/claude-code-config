---
name: atlassian-companion
description: "Companion skill for the `acli` Atlassian command-line tool. Provides correct flag patterns, JQL quirks, ADF description handling, and bulk-operation guardrails for Jira work items. Load this skill before running any `acli jira` command to avoid malformed calls and accidental bulk writes."
effort: low
---

# Atlassian CLI Companion

Reference guide for driving Jira through `acli`, Atlassian's official CLI. Load the relevant
reference before running commands so you use the right flags and do not fire a bulk write by
accident.

Scope: **Jira only.** `acli` cannot create, update, delete, or search Confluence pages. Its
`confluence page` command has exactly one subcommand, `view --id`. If a task needs Confluence
writes, say so and stop; do not improvise with `curl` unless the user asks for it.

## When to Use

- Before creating, editing, searching, transitioning, or commenting on Jira work items
- When a JQL query returns unexpected results
- When an `acli` command fails and you are about to retry with different flags

## Vocabulary

`acli` calls issues **work items**. The command noun is `workitem`, not `issue`. Everything
lives under `acli jira workitem <verb>`.

## Prerequisites

Check authentication before the first write of a session:

```bash
acli auth status
```

If it prints `unauthorized`, stop and ask the user to run `acli auth login` themselves. It is an
interactive OAuth flow and you cannot complete it for them.

`acli auth switch` selects between multiple authenticated accounts or sites. If the user works
across more than one Atlassian site, confirm the active one before writing.

## Quick Reference: Common Pitfalls

### Descriptions are plain text or ADF, never markdown

`--description` takes a plain string or Atlassian Document Format JSON. There is no markdown
conversion layer. Markdown syntax written into a description arrives as literal characters:
`## Steps` renders as the text `## Steps`, not a heading.

For anything with structure (headings, lists, code blocks), build ADF and pass it through
`--description-file` or `--from-json`. See `references/jira-crud.md`.

### `--jql` on a write command is a bulk operation

`edit`, `transition`, `delete`, `assign`, and `clone` all accept `--jql`. A typo in the query
hits every matching work item in the project. Before any `--jql` write:

1. Run the same query through `acli jira workitem search --jql "..." --count` and report the
   number to the user.
2. Never pass `--yes` on a `--jql` write unless the user has seen that count and approved it.

`--yes` on a `--key` write with one or two explicit keys is fine.

### Priority has no flag

There is no `--priority` on `create` or `edit`. Setting priority requires the JSON path with
`additionalAttributes`, and that is unverified against a live instance. Ask the user rather than
guessing at the field shape.

### Transitions go by status name, not ID

`acli jira workitem transition --key KEY-1 --status "Done"` takes the target status directly.
There is no command that lists available transitions, so an invalid status name is discovered
only when the command fails. Read the current status from `acli jira workitem view` first.

### `view` omits comments by default

The default field set is `key,issuetype,summary,status,assignee,description`. Ask for comments
explicitly: `--fields summary,comment`, or use `acli jira workitem comment list --key KEY-1`.

## Process

### Step 0: Resolve Project Context

Before any Jira operation, determine the Jira project key for the current working directory. Do
NOT hardcode a project key. Look it up:

1. Search the local project's `CLAUDE.md` files (both repo-level and `.claude/CLAUDE.md`) for a
   Jira project declaration (e.g. `project to reference is WPD`, `project_key: XYZ`)
2. Check for a `## Jira Integration` section, which may also declare labeling rules per repo
3. If no project key is found, ask the user

Use the discovered key for `--project` and in JQL. If the project's CLAUDE.md specifies **labels
by repo** (e.g. `react-native-wavelydx-v2` maps to `v2-wrapper`), apply those labels with
`--label` when creating.

### Step 1: Identify the Operation

- Work item create, view, edit, delete, comments, attachments: `references/jira-crud.md`
- Search and JQL patterns: `references/jira-search.md`
- Transitions, links, sprints, boards, projects, bulk operations: `references/jira-workflow.md`

### Step 2: Load the Reference

Read the reference before composing the command. Most failures are wrong flag names or a missing
required flag, not API errors.

### Step 3: Execute

Add `--json` when you need to parse the result rather than show it to the user. Pipe through
`jq` to extract fields.

## Verification Status

Everything documented in this skill and its references was read from `acli --help` output on
version **1.3.22-stable**. None of it has been executed against a live Atlassian instance,
because `acli` was unauthenticated when the skill was written.

Flag names, subcommand names, and JSON templates from `--generate-json` are therefore reliable.
Runtime behavior is not. These specific claims are unverified and are marked again where they
appear:

- Whether `edit --labels` replaces the label set or appends to it
- Whether `additionalAttributes` accepts system fields such as `priority`
- Whether `--parent` links a Story to an Epic, or only a sub-task to its parent
- Whether a plain-text `--description` is accepted as-is or must be ADF

When one of these comes up, run the command on a low-stakes work item first and check the
result, then correct this skill.
