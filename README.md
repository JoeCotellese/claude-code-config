# Claude Code Config

A collection of custom extensions for Claude Code including skills, slash commands, and hooks.

The centerpiece is the **feature development loop** — seven phase skills that drive an issue
from idea to merged code, with reverse edges so a problem routes back to the phase that owns
it instead of getting patched downstream.

```
/spec → /ready → /ui-design → /implement → /verify → /submit → merged
                                                  ↘ /retro ↗
```

Two gates make it work. The **Definition of Ready** (`/ready`) refuses to let an issue into
implementation until its acceptance criteria are observable and an acceptance test exists. The
**Definition of Done** (`/verify`) refuses to call it finished until that test passes and every
criterion has something reporting on it.

**→ [`plugins/dev-jawn/skills/WORKFLOW.md`](plugins/dev-jawn/skills/WORKFLOW.md)** documents the
whole thing: a diagram, the seven loops with their exit conditions and caps, both definitions in
full, and what each phase does.

The loop ships as the **dev-jawn plugin** (`plugins/dev-jawn/`), a single toggleable unit. See
[The dev-jawn workflow plugin](#the-dev-jawn-workflow-plugin) below.

## Installation

This repository uses a Makefile to manage symlinks to `~/.claude`. Unlike directory-level symlinks, this approach creates individual symlinks for each skill/agent/etc., allowing third-party additions to coexist without polluting the repo.

### Install symlinks

```bash
cd ~/git/claude-code-config
make install
```

This creates symlinks in `~/.claude/` for all managed configuration files while preserving any third-party skills or extensions you've installed.

### Check status

```bash
make status
```

Shows which items are managed (symlinked to this repo) vs third-party (installed directly).

### Uninstall symlinks

```bash
make uninstall
```

Removes only the managed symlinks, preserving third-party items.

### Update after pulling changes

```bash
cd ~/git/claude-code-config
git pull
# Symlinks update automatically since they point to the repo files
```

## The dev-jawn workflow plugin

The feature development loop (the eight phase skills, `WORKFLOW.md`, and the `cpr` command) is
packaged as a Claude Code plugin under `plugins/dev-jawn/` so the whole workflow can be toggled
as one unit. The workflow policy that used to live in `CLAUDE.md`'s "Git Workflow" section now
ships with the plugin as a `UserPromptSubmit` hook (`hooks/workflow-policy.sh`): disable the
plugin and the rules leave context along with the skills, so nothing dangles.

Because the loop skills now come from the plugin rather than `~/.claude/skills/`, they are **not**
symlinked by `make install`. Install and toggle them with the plugin commands instead:

```bash
# one-time: point Claude Code at this repo as a marketplace, then install dev-jawn
claude plugin marketplace add ~/git/claude-code-config
claude plugin install dev-jawn

claude plugin disable dev-jawn   # swap the workflow off
claude plugin enable  dev-jawn   # swap it back on
```

### Migrating from the symlinked skills

If you previously ran `make install`, the eight phase skills, `WORKFLOW.md`, and `cpr.md` are
still symlinked into `~/.claude/` and now point at files that moved into the plugin, leaving
dangling links. Remove them once, then install the plugin:

```bash
make prune            # removes broken symlinks in the managed ~/.claude dirs
claude plugin install dev-jawn
```

`ios-ui-tester` and the language `docs/` stay in the base repo; the plugin references them by
skill name and by `~/.claude/docs/` path, so keep `make install` for the rest of the config.

## Structure

```
claude-code-config/
├── skills/              # Custom skill packages (base, symlinked via make install)
├── plugins/dev-jawn/    # The feature development loop, as a toggleable plugin
├── agents/              # Agent configurations
├── commands/            # Slash command definitions
├── docs/                # Language/tech standards
├── scripts/             # Helper scripts
├── output-styles/       # Output formatting
├── CLAUDE.md            # Global instructions
├── statusline-command.sh
├── Makefile             # Install/uninstall automation
├── README.md            # This file
└── .gitignore
```

After installation, `~/.claude/skills/` will contain:
- Your skills as symlinks pointing to this repo
- Third-party skills as real directories (not tracked by git)

## Skills

Custom skills extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

### The feature development loop

Ships as the [dev-jawn plugin](#the-dev-jawn-workflow-plugin), not as base symlinks. Six phases
plus a reverse edge. See
[`plugins/dev-jawn/skills/WORKFLOW.md`](plugins/dev-jawn/skills/WORKFLOW.md) for how they fit
together, the Definition of Ready, and the Definition of Done.

| Skill | Description |
|-------|-------------|
| **spec** | Specification phase — product, UX, and architecture into a filed issue. Also repairs an issue that failed the Definition of Ready |
| **ready** | Definition of Ready gate — audits seven criteria, repairs what it can, derives the acceptance test, prints `DOR VERDICT` |
| **ui-design** | Builds the real view as a prototype, drives it, and runs a fresh-context design committee. UI features only |
| **implement** | TDD implementation under a goal whose exit condition is the Definition of Done |
| **verify** | Definition of Done runner — unit suite plus the acceptance test, reconciles every criterion to its channel, prints `DOD VERDICT` |
| **submit** | Code review committee, then PR/MR, review iteration, and merge |
| **retro** | Reverse edge — names the gate that missed a failure and amends it |

### Everything else

| Skill | Description |
|-------|-------------|
| **kaizen** | Continuous improvement practices |
| **learnings** | Curate durable project learnings into a shared, opt-in `LEARNINGS.md` |
| **managing-productivity** | Hybrid GTD + Energy/Time filtering system in Todoist with calendar integration |
| **product-manager** | Unified PM skill for prioritization (RICE, Kano, MoSCoW) and specifications (PRDs, user stories) across platforms |

## Commands

Slash commands for quick, repeatable actions.

| Command | Description |
|---------|-------------|
| **cpr** | Code review |

> Note: the `summarize` command was removed — session recap is now handled by [claude-mem](https://github.com/thedotmack/claude-mem), which auto-captures observations and provides `/claude-mem:timeline-report` for narrative summaries.

## Agents

Custom agent configurations for specialized tasks.

| Agent | Description |
|-------|-------------|
| **git-release-tagger** | Git release tagging automation |
| **product-manager-apple** | Apple platform product management |
| **swift-swiftui-reviewer** | Swift/SwiftUI code review |
| **xcode-release-manager** | Xcode release management |

## Status Line

A custom status line script that displays contextual information at the bottom of Claude Code, styled with Dracula theme colors.

### What it shows

- **Directory** - Current working directory name (green)
- **Git branch** - Branch name when in a git repo (pink)
- **Dirty indicator** - Red asterisk (`*`) if there are uncommitted changes
- **Context usage** - Percentage of context window used (yellow)

Example output: `claude-code-config on main* 42%`

### Setup

Add to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
}
```

The `make install` command symlinks the script to `~/.claude/`, so this configuration will work after installation.

## Hooks

Claude Code hooks live in `~/.claude/settings.json`, which this repo deliberately does **not** manage (Claude Code rewrites `permissions.allow` on every permission grant, so symlinking the whole file would churn constantly). Instead, hook *behavior* is versioned here as standalone scripts under `scripts/`, and `settings.json` calls them via their symlinked paths.

### Atlassian companion reminder

`scripts/atlassian-companion-reminder.sh` is a `PreToolUse` hook body that prints a reminder to load the `atlassian-companion` skill before any `acli` command. It exists because Jira work-item commands take flags that are easy to get subtly wrong, and because the write verbs accept `--jql`, which turns a typo into a bulk edit across a whole project. The skill documents both.

The matcher is `Bash`, so the hook fires on every Bash call and the script decides for itself whether the command invokes `acli`. Non-matching commands produce no output. It needs `jq` on `PATH`.

After `make install`, add this block to `~/.claude/settings.json` (once, per machine):

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash ~/.claude/scripts/atlassian-companion-reminder.sh"
        }
      ]
    }
  ]
}
```

Verify it works. The first prints the reminder JSON; the second prints nothing:

```bash
echo '{"tool_input":{"command":"acli jira workitem view PROJ-1"}}' | bash ~/.claude/scripts/atlassian-companion-reminder.sh | jq .
echo '{"tool_input":{"command":"git status"}}' | bash ~/.claude/scripts/atlassian-companion-reminder.sh
```

## Benefits of This Approach

1. **Clean separation**: Your skills are symlinks, third-party skills are real directories
2. **No pollution**: Installing a third-party skill never touches your repo
3. **Easy identification**: `ls -la ~/.claude/skills/` shows which are yours (symlinks) vs third-party (real)
4. **Simple updates**: `git pull` in repo automatically updates symlinked content
5. **No dependencies**: Just `make` - no need for GNU Stow
