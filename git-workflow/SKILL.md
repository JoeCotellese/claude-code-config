---
name: git-workflow
description: Enforce branch-first git workflow. Use this skill when starting any new feature or fix, committing code, or creating pull requests. Prevents direct commits to main branch and ensures proper issue tracking through branch names, commit messages, and PR descriptions.
---

# Git Workflow

## Overview

Enforce a branch-first development workflow that prevents direct commits to main/master branches and ensures all work is properly tracked through issues, descriptive branches, and well-formatted commits and pull requests.

## When to Use This Skill

Invoke this skill automatically when:
- User mentions working on an issue number (e.g., "Let's work on #123")
- User wants to start a new feature or fix
- User is about to commit code
- User wants to create a pull request
- User asks about git workflow or branching

## Core Workflow

### 1. Starting Work (Branch Creation)

**CRITICAL**: NEVER allow work to begin without first creating a proper branch.

When user mentions working on an issue or feature:

1. **Identify the issue number** - If not provided, ask for it
2. **Determine branch type**:
   - `feature/` - New functionality
   - `fix/` - Bug fixes
   - `hotfix/` - Urgent production fixes
3. **Create descriptive branch name**: `{type}/{issue-number}-{brief-description}`
4. **Use the helper script**:

```bash
bash scripts/create_feature_branch.sh <issue-number> <type> <description>
```

**Example**:
```bash
# User says: "Let's work on issue #70"
bash scripts/create_feature_branch.sh 70 feature applies-condition-field
# Creates: feature/70-applies-condition-field
```

The script will:
- Fetch latest from remote
- Switch to main branch
- Pull latest changes
- Create and checkout new branch
- Confirm ready to work

**Manual alternative** (if script unavailable):
```bash
git fetch origin
git checkout main
git pull origin main
git checkout -b feature/123-brief-description
```

### 2. Making Commits

When ready to commit changes:

1. **Verify not on main branch** - The pre-commit hook will block, but check first
2. **Review changes**: `git status` and `git diff`
3. **Stage relevant files**: `git add <files>`
4. **Craft proper commit message** - See references/commit_message_format.md for details

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
Any item can now apply conditions via JSON without code changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Commit types**: Fix, Add, Update, Refactor, Remove, Docs, Test, Chore

See `references/commit_message_format.md` for extensive examples and guidelines.

### 3. Creating Pull Requests

When work is complete and ready for review:

1. **Ensure all changes are committed**
2. **Run full test suite** - Never create PR/MR with failing tests
3. **Push branch to remote**: `git push -u origin <branch-name>`
4. **Detect platform and create PR/MR**:

First detect the platform:
```bash
PLATFORM=$(bash scripts/detect_git_platform.sh)
```

**For GitHub** (use `gh`):
```bash
gh pr create --title "Fix #70: Brief description" --body "$(cat <<'EOF'
## Summary
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Changes
- **file1.py**: What changed and why
- **file2.py**: What changed and why

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed
- [x] No new warnings or errors

## Related Issues
Fixes #70

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**For GitLab** (use `glab`):
```bash
glab mr create --title "Fix #70: Brief description" --description "$(cat <<'EOF'
## Summary
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Changes
- **file1.py**: What changed and why
- **file2.py**: What changed and why

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed
- [x] No new warnings or errors

## Related Issues
Fixes #70

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

See `references/pr_template.md` for complete examples.

### 4. After PR Merge

Once PR is merged to main:

1. **Switch back to main**: `git checkout main`
2. **Pull latest changes**: `git pull origin main`
3. **Delete feature branch** (optional):
   ```bash
   git branch -d feature/70-applies-condition-field
   git push origin --delete feature/70-applies-condition-field
   ```

## Protection: Pre-Commit Hook

To prevent accidental commits to main/master, install the pre-commit hook:

```bash
bash scripts/setup_git_hooks.sh
```

The hook will:
- Block any commits to main or master branches
- Display helpful error message with proper workflow
- Allow bypass with `--no-verify` flag (emergencies only)

**Install once per repository**. The hook is stored in `.git/hooks/pre-commit`.

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
    ↓ NO → Create branch using create_feature_branch.sh
    ↓ YES → Verify branch matches issue, continue
    ↓
User makes code changes
    ↓
Ready to commit?
    ↓ YES
Verify not on main (check with git branch)
    ↓
Stage changes (git add)
    ↓
Create commit with proper format (see references/commit_message_format.md)
    ↓
Use HEREDOC format to preserve message formatting
    ↓
Commit successful
    ↓
More changes needed?
    ↓ NO → Ready for PR
    ↓
Run tests
    ↓
Tests pass?
    ↓ YES
Push branch to remote
    ↓
Create PR with gh pr create (see references/pr_template.md)
    ↓
Done
```

## Common Patterns

### Pattern 1: User mentions issue number
```
User: "Let's work on issue #123"
Assistant:
1. Check current branch
2. If on main → run create_feature_branch.sh 123 feature <description>
3. If on feature branch → verify it matches #123, continue
4. Proceed with work
```

### Pattern 2: User wants to commit
```
User: "Ready to commit"
Assistant:
1. Run git status to see changes
2. Verify not on main branch
3. Run git diff to review changes
4. Ask user to confirm changes to commit (or stage all)
5. Create commit message following format (see references/)
6. Commit using HEREDOC format
7. Confirm commit successful
```

### Pattern 3: User wants to create PR/MR
```
User: "Create a PR" or "Create an MR"
Assistant:
1. Verify all changes committed (git status clean)
2. Remind user to run tests
3. Get test results confirmation
4. Push branch if not pushed
5. Detect platform: bash scripts/detect_git_platform.sh
6. Create PR/MR with gh pr create (GitHub) or glab mr create (GitLab)
7. Use proper PR format (see references/pr_template.md)
8. Return PR/MR URL
```

### Pattern 4: Emergency main commit needed
```
User: "I need to commit directly to main"
Assistant:
1. Warn about dangers of main commits
2. Suggest creating hotfix branch instead
3. If user insists:
   - Document why in commit message
   - Use --no-verify flag to bypass hook
   - Push immediately after commit
```

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

# Detect platform (github/gitlab/unknown)
bash scripts/detect_git_platform.sh

# Create branch
bash scripts/create_feature_branch.sh <issue> <type> <desc>

# Stage changes
git add <files>  # specific files
git add .        # all changes

# Commit (use HEREDOC)
git commit -m "$(cat <<'EOF'
Message here
EOF
)"

# Push branch
git push -u origin <branch-name>

# Create PR (GitHub)
gh pr create --title "..." --body "$(cat <<'EOF'
...
EOF
)"

# Create MR (GitLab)
glab mr create --title "..." --description "$(cat <<'EOF'
...
EOF
)"
```

## Resources

### scripts/
- `create_feature_branch.sh` - Creates properly named feature/fix/hotfix branches
- `pre_commit_hook.sh` - Blocks commits to main/master (installed by setup script)
- `setup_git_hooks.sh` - Installs the pre-commit hook (run once per repo)
- `detect_git_platform.sh` - Detects GitHub vs GitLab to use correct CLI tool (gh/glab)

### references/
- `commit_message_format.md` - Extensive examples and guidelines for commit messages
- `pr_template.md` - Complete PR format with real examples from projects

All scripts are executable and include usage instructions. Reference files provide detailed examples from real-world usage.
