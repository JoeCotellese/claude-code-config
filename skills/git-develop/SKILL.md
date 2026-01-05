---
name: git-develop
description: This skill enforces development discipline during active work on issues. INVOKE IMMEDIATELY when user says "work on issue", "fix issue", "implement", "let's work on #", or mentions any issue number. Handles branch creation, atomic commits, and ensures tests stay with their related code changes. Prevents direct commits to main branch.
---

# Git Develop

## Overview

Enforce development discipline with proper branching, atomic commits, and co-located tests. This skill focuses exclusively on the development phase—from starting work on an issue through committing changes. It does NOT handle submission for review (see git-submit skill for that).

## When to Use This Skill

Invoke this skill automatically when:
- User mentions working on an issue number (e.g., "Let's work on #123")
- User wants to start a new feature or fix
- User is about to commit code
- User asks about git workflow or branching during development

## Core Principle: Keep Related Changes Together

**CRITICAL**: Features and their tests belong in the same branch and commits.

When implementing a feature or fix:
1. Code changes and test updates go in the SAME branch
2. Before committing UI changes, check for affected tests: `rg "<element_id>" scripts/uitests/`
3. Never separate a feature from its test into different branches/MRs

## Workflow

### 1. Starting Work (Branch Creation)

**CRITICAL**: NEVER allow work to begin without first creating a proper branch.

When user mentions working on an issue:

1. **Identify the issue number** - If not provided, ask for it
2. **Determine branch type**:
   - `feature/` - New functionality
   - `fix/` - Bug fixes
   - `hotfix/` - Urgent production fixes
3. **Create branch using the helper script**:

```bash
bash ~/.claude/skills/git-develop/scripts/create_feature_branch.sh <issue-number> <type> <description>
```

**Example**:
```bash
# User says: "Let's work on issue #70"
bash ~/.claude/skills/git-develop/scripts/create_feature_branch.sh 70 feature applies-condition-field
# Creates: feature/70-applies-condition-field
```

The script will:
- Fetch latest from remote
- Switch to main branch
- Pull latest changes
- Create and checkout new branch
- Confirm ready to work

### 2. Making Commits

When ready to commit changes:

1. **Verify not on main branch** - The pre-commit hook will block, but check first
2. **Review changes**: `git status` and `git diff`
3. **Check for related tests** (especially for UI changes):
   ```bash
   # Find tests that reference modified UI elements
   rg "<element_id>" scripts/uitests/
   ```
4. **Stage relevant files**: `git add <files>`
5. **Create commit with proper format** - See `references/commit_message_format.md`

**Commit message format**:
```
<Type> #<issue>: <Brief description under 72 chars>

<Optional detailed explanation of WHY>
<Bullet points for multi-part changes>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Commit using HEREDOC** (to preserve formatting):
```bash
git commit -m "$(cat <<'EOF'
Fix #70: Use applies_condition field instead of hardcoded string checks

- Add "applies_condition": "on_fire" to alchemists_fire in items.json
- Refactor use_combat_attack_item() to read applies_condition field
- Remove hardcoded "alchemist" string matching

This follows data-driven design principle (ARCHITECTURE.md).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Commit types**: Fix, Add, Update, Refactor, Remove, Docs, Test, Chore

### Commit Quality Standards

**CRITICAL**: Apply these standards consistently on every commit.

#### 1. Always Use Type Prefixes
Every commit MUST start with a type prefix. No exceptions.

✅ **Correct**:
- `Fix #70: Resolve memory leak in image cache`
- `Add #123: User profile settings page`
- `Refactor #45: Extract validation logic to separate module`

❌ **Incorrect**:
- `Resolve memory leak in image cache` (missing type)
- `misc commits` (meaningless)
- `bump version` (missing type and context)

#### 2. Always Reference Issues
Every commit MUST reference an issue number. If there's no issue, create one first or use `Chore:` for maintenance tasks.

#### 3. One Logical Change Per Commit (Atomic Commits)
Each commit should contain exactly one logical change. If you find yourself using "and" in a commit message, split it into two commits.

✅ **Correct** (two separate commits):
```
Chore: Bump version to 2025.11.3
Fix #99: Correct Algolia index name for production
```

❌ **Incorrect** (bundled changes):
```
Bump version to 2025.11.3 and fix Algolia index name
```

#### 4. Commit Message Body Explains "Why"
The subject line says WHAT changed. The body explains WHY.

## Protection: Git Hooks

Install git hooks to enforce workflow standards:

```bash
bash ~/.claude/skills/git-develop/scripts/setup_git_hooks.sh
```

This installs two hooks:

### Pre-Commit Hook
- Blocks any commits to main or master branches
- Displays helpful error message with proper workflow

### Commit-Msg Hook
Validates every commit message for:
- **Type prefix** - Must start with Fix, Add, Update, Refactor, Remove, Docs, Test, or Chore
- **Issue reference** - Must include `#123` (except Chore commits)
- **Length limit** - Subject line max 72 characters

**Install once per repository**. Hooks are stored in `.git/hooks/`.

## Workflow Decision Tree

```
User starts conversation about work
    ↓
Is user working on a specific issue/feature?
    ↓ YES
Do we have an issue number?
    ↓ NO → Ask for issue number
    ↓ YES
Are we already on a feature branch?
    ↓ NO → Create branch using ~/.claude/skills/git-develop/scripts/create_feature_branch.sh
    ↓ YES → Verify branch matches issue, continue
    ↓
User makes code changes
    ↓
Ready to commit?
    ↓ YES
Check for related tests (especially UI)
    ↓
Verify not on main
    ↓
Stage changes (git add)
    ↓
Create atomic commit with proper format
    ↓
Commit successful
    ↓
More changes needed?
    ↓ YES → Continue development
    ↓ NO → STOP (use git-submit when ready for review)
```

## What This Skill Does NOT Do

This skill focuses only on development. It does NOT:
- ❌ Push to remote
- ❌ Create merge/pull requests
- ❌ Merge branches
- ❌ Clean up branches

For submission and review, use the **git-submit** skill.

## Quick Reference

### Branch Naming
- `feature/123-brief-desc` - New features
- `fix/456-brief-desc` - Bug fixes
- `hotfix/789-brief-desc` - Urgent fixes

### Commit Format
```
<Type> #<issue>: <Brief description>

<Why explanation>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Helpful Commands
```bash
# Check current branch
git branch --show-current

# See what would be committed
git status
git diff

# Create branch
bash ~/.claude/skills/git-develop/scripts/create_feature_branch.sh <issue> <type> <desc>

# Stage changes
git add <files>  # specific files
git add .        # all changes

# Find related tests
rg "<element_id>" scripts/uitests/

# Commit (use HEREDOC)
git commit -m "$(cat <<'EOF'
Message here
EOF
)"
```

## Resources

All resources are located in `~/.claude/skills/git-develop/`.

### scripts/
- `create_feature_branch.sh` - Creates properly named feature/fix/hotfix branches
- `pre_commit_hook.sh` - Blocks commits to main/master (installed by setup script)
- `commit_msg_hook.sh` - Validates commit message format (type, issue ref, length)
- `setup_git_hooks.sh` - Installs all git hooks (run once per repo)

### references/
- `commit_message_format.md` - Extensive examples and guidelines for commit messages
