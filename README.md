# Claude Code Config

A collection of custom extensions for Claude Code including skills, slash commands, and hooks.

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

## Structure

```
claude-code-config/
├── skills/              # Custom skill packages
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

| Skill | Description |
|-------|-------------|
| **git-workflow** | Enforce branch-first git workflow - prevents direct commits to main branch |
| **git-submit** | Submit changes through proper PR workflow |
| **kaizen** | Continuous improvement practices |
| **managing-productivity** | Hybrid GTD + Energy/Time filtering system in Todoist with calendar integration |
| **product-manager** | Unified PM skill for prioritization (RICE, Kano, MoSCoW) and specifications (PRDs, user stories) across platforms |
| **react-native-reviewer** | React Native code review |

## Commands

Slash commands for quick, repeatable actions.

| Command | Description |
|---------|-------------|
| **cpr** | Code review |
| **summarize** | Summarize content |

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

`scripts/atlassian-companion-reminder.sh` is a `PreToolUse` hook body that prints a reminder to load the `atlassian-companion` skill before any `mcp-atlassian` tool call. It exists because Jira/Confluence MCP calls silently return wrong results when parameters are shaped incorrectly (e.g. reporter by email instead of display name), and the skill documents those quirks.

After `make install`, add this block to `~/.claude/settings.json` (once, per machine):

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "mcp__mcp-atlassian__.*",
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

Verify it works:

```bash
bash ~/.claude/scripts/atlassian-companion-reminder.sh | jq .
```

## Benefits of This Approach

1. **Clean separation**: Your skills are symlinks, third-party skills are real directories
2. **No pollution**: Installing a third-party skill never touches your repo
3. **Easy identification**: `ls -la ~/.claude/skills/` shows which are yours (symlinks) vs third-party (real)
4. **Simple updates**: `git pull` in repo automatically updates symlinked content
5. **No dependencies**: Just `make` - no need for GNU Stow
