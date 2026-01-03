# Claude Code Config

A collection of custom extensions for Claude Code including skills, slash commands, and hooks.

## Structure

```
claude-code-config/
├── skills/      # Custom skills with specialized knowledge and workflows
├── commands/    # Slash commands for quick actions
└── hooks/       # Event-triggered automation
```

## Skills

Custom skills extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

| Skill | Description |
|-------|-------------|
| **filing-skill** | Process and organize scanned business and personal documents |
| **git-workflow** | Enforce branch-first git workflow - prevents direct commits to main branch |
| **ios-ui-tester** | iOS UI testing with SwiftUI and simulator automation |
| **managing-productivity** | Hybrid GTD + Energy/Time filtering system in Todoist with calendar integration |
| **product-manager-apple** | Define product requirements, write user stories, and analyze features for Apple platforms |
| **python-code-reviewer** | Comprehensive Python code review for quality, security, and performance |
| **swift-architect** | Swift/SwiftUI architecture consulting and design decisions |

## Commands

Slash commands for quick, repeatable actions. *(Coming soon)*

## Hooks

Event-triggered automation for Claude Code workflows. *(Coming soon)*

## Installation

Symlink skills into `~/.claude/skills/`:

```bash
ln -s /path/to/claude-code-config/skills/skill-name ~/.claude/skills/skill-name
```
