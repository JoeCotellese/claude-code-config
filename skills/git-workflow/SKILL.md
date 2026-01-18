---
name: git-workflow
description: |
  Enforce branch-first git workflow. INVOKE IMMEDIATELY (before writing ANY code) when:
  - User says "implement", "implement the plan", "implement this feature"
  - User says "work on", "work on issue", "let's work on #"
  - User says "fix", "fix issue", "fix bug"
  - User mentions any issue number (#123, issue 45, etc.)
  - User says "start coding", "let's build", "build this"
  - User provides a plan and expects implementation

  Also use when committing code, creating pull requests, or "ship it".

  CRITICAL: If on main branch when implementation starts, CREATE FEATURE BRANCH FIRST.
  This skill prevents direct commits to main branch.
---

# Git Workflow

## Pre-Flight Check (DO THIS FIRST)

**Before writing ANY code**, run this check:

```bash
git branch --show-current
```

If the output is `main` or `master`:
1. **STOP** - Do not write any code yet
2. Ask user for issue number if not provided
3. Create feature branch: `bash scripts/create_feature_branch.sh <issue> <type> <desc>`
4. Only THEN proceed with implementation

This check is MANDATORY. Never skip it.

## Overview

Enforce a branch-first development workflow that prevents direct commits to main/master branches and ensures all work is properly tracked through issues, descriptive branches, and well-formatted commits and pull requests.

## When to Use This Skill

Invoke this skill automatically when:
- User mentions working on an issue number (e.g., "Let's work on #123")
- User wants to start a new feature or fix
- User is about to commit code
- User wants to create a pull request
- User asks about git workflow or branching
- User says "ship it", "let's ship this", or "ready to merge" (triggers Pattern 5: complete shipping workflow)

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

✅ **Correct**:
- `Fix #226: Spotlight recipe indexing`
- `Chore: Update dependencies to latest versions`

❌ **Incorrect**:
- `Fix Spotlight recipe indexing` (no issue reference)
- `Update dependencies` (no type, no context)

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

#### 4. Clean Up Branches After Merge
After a PR/MR is merged, ALWAYS delete both local and remote feature branches:

```bash
# Delete local branch
git branch -d feature/123-description

# Delete remote branch (if not auto-deleted by merge)
git push origin --delete feature/123-description
```

Stale branches create clutter and confusion. Clean up immediately after merge.

#### 5. Commit Message Body Explains "Why"
The subject line says WHAT changed. The body explains WHY.

✅ **Correct**:
```
Fix #231: Track recipe_count as user property in analytics

The recipe count helps segment users by engagement level
for targeted feature rollouts and A/B testing.

Uses removeDuplicates() to avoid unnecessary analytics calls
when count hasn't actually changed.
```

❌ **Incorrect**:
```
Fix #231: Track recipe_count as user property in analytics

Added a Combine pipeline that updates the recipe_count.
```
(Body just restates the "what", not the "why")

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

## Protection: Git Hooks

Install git hooks to enforce workflow standards:

```bash
bash scripts/setup_git_hooks.sh
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

**Example rejections:**
```
❌ "bump version"           → Missing type prefix
❌ "Fix the bug"            → Missing issue reference
❌ "Fix #123 Really long... → Over 72 characters
```

**Valid formats:**
```
✅ Fix #123: Brief description
✅ Add #456: New feature description
✅ Chore: Maintenance task (no issue required)
```

**Install once per repository**. Hooks are stored in `.git/hooks/`.

To bypass hooks in emergencies (not recommended):
```bash
git commit --no-verify
```

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

### Pattern 5: Ship It (Complete Feature Workflow)
```
User: "ship it" or "let's ship this feature" or "ready to merge"
```

This pattern chains all shipping steps into one automated workflow:

**Step 1: Verify Branch State**
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "ERROR: Cannot ship from main/master. Create a feature branch first."
    exit 1
fi
git status
```

**Step 2: Language-Aware Code Review (BLOCKING)**

Detect the project language and run the appropriate code reviewer:

```bash
# Check for Python files
if git diff --name-only --diff-filter=ACMR HEAD "*.py" | head -1 | grep -q .; then
    # Python project - invoke python-code-reviewer skill
    python ~/.claude/skills/python-code-reviewer/scripts/run_checks.py .
    # Then perform manual review per the skill's checklist
fi

# Check for Swift files
if git diff --name-only --diff-filter=ACMR HEAD "*.swift" | head -1 | grep -q .; then
    # Swift project - invoke swift-swiftui-reviewer Task agent
    # Review Swift/SwiftUI code for best practices
fi
```

**CRITICAL**: If code review finds critical issues, STOP the workflow immediately.
Report the issues to the user and wait for fixes before continuing.

**Step 3: Stage and Commit**
```bash
git add -A
git status
git diff --cached --stat
```

Create commit with proper format (see Pattern 2).

**Step 4: Push to Remote**
```bash
git push -u origin $(git branch --show-current)
```

If rejected due to upstream changes:
```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if needed
git push -u origin $(git branch --show-current)
```

**Step 5: Create PR**

Use gh pr create (see Pattern 3 for format).

**Step 6: Merge PR**
```bash
# Wait for CI if configured
gh pr checks

# Merge with squash and auto-delete remote branch
gh pr merge --squash --delete-branch
```

**Step 7: Return to Main**
```bash
git checkout main
git pull origin main

# Delete local feature branch
git branch -d <branch-name>
```

**Step 8: Confirm Success**

Report to user:
- Merged commit hash
- PR number and URL
- Confirmation branches cleaned up
- Current state: on main, up to date

**Error Handling:**
- Code review critical issues → STOP, report issues, wait for fix
- Push rejected → Attempt rebase, if conflicts STOP
- PR creation fails → Report error (gh auth issue, existing PR, etc.)
- Merge fails → Report error (CI failing, conflicts, branch protection)

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
- `commit_msg_hook.sh` - Validates commit message format (type, issue ref, length)
- `setup_git_hooks.sh` - Installs all git hooks (run once per repo)
- `detect_git_platform.sh` - Detects GitHub vs GitLab to use correct CLI tool (gh/glab)

### references/
- `commit_message_format.md` - Extensive examples and guidelines for commit messages
- `pr_template.md` - Complete PR format with real examples from projects

All scripts are executable and include usage instructions. Reference files provide detailed examples from real-world usage.
