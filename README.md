# Claude Code Config

A collection of custom extensions for Claude Code including skills, slash commands, and hooks.

## Installation

This repository uses [GNU Stow](https://www.gnu.org/software/stow/) to manage symlinks to `~/.claude`.

### Prerequisites

Install GNU Stow via Homebrew:
```bash
brew install stow
```

### Install symlinks

```bash
cd ~/git/claude-code-config
stow -t ~ claude
```

This creates symlinks in `~/.claude/` for all managed configuration files.

### Uninstall symlinks

```bash
cd ~/git/claude-code-config
stow -t ~ -D claude
```

### Update after pulling changes

```bash
cd ~/git/claude-code-config
git pull
stow -t ~ -R claude   # Restow (removes then recreates symlinks)
```

## Structure

```
claude-code-config/
├── claude/              # Stow package (symlinked to ~/.claude)
│   └── .claude/
│       ├── agents/      # Custom agent configurations
│       ├── CLAUDE.md    # Global instructions
│       ├── commands/    # Slash commands for quick actions
│       ├── docs/        # Language-specific standards
│       ├── output-styles/
│       ├── scripts/
│       ├── settings.json
│       ├── skills/      # Custom skills
│       └── statusline-command.sh
├── README.md
└── .claude/             # Local settings (gitignored)
```

## Skills

Custom skills extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

| Skill | Description |
|-------|-------------|
| **filing-skill** | Process and organize scanned business and personal documents |
| **git-workflow** | Enforce branch-first git workflow - prevents direct commits to main branch |
| **ios-ui-tester** | iOS UI testing with SwiftUI and simulator automation |
| **managing-productivity** | Hybrid GTD + Energy/Time filtering system in Todoist with calendar integration |
| **product-manager** | Unified PM skill for prioritization (RICE, Kano, MoSCoW) and specifications (PRDs, user stories) across platforms |
| **product-manager-apple** | Define product requirements, write user stories, and analyze features for Apple platforms |
| **python-code-reviewer** | Comprehensive Python code review for quality, security, and performance |
| **swift-architect** | Swift/SwiftUI architecture consulting and design decisions |

## Commands

Slash commands for quick, repeatable actions. *(Coming soon)*

## Hooks

Event-triggered automation for Claude Code workflows. *(Coming soon)*
