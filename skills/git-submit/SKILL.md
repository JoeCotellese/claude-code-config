---
name: git-submit
description: This skill submits completed work for human review. Use ONLY when explicitly requested with phrases like "ready for review", "create MR", "submit for review", "push this", or "open a PR". Creates merge/pull requests and STOPS at the MR URL. NEVER auto-merges. Human code review must happen first.
---

# Git Submit

## Overview

Submit completed work for human review. This skill handles pushing branches and creating merge/pull requests. It deliberately STOPS after creating the MR and reporting the URL—merging is a human decision that happens after code review.

## When to Use This Skill

**ONLY invoke when user explicitly requests submission:**
- "ready for review"
- "create MR" / "create PR"
- "submit for review"
- "push this"
- "open a pull request"

**DO NOT invoke automatically.** Development work uses the git-develop skill. This skill is only for the explicit handoff to human review.

## Core Principle: Human Review Gate

**CRITICAL**: Code review by humans must happen before any merge.

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE HUMAN GATE                               │
│                                                                  │
│   Developer Work  ──→  Create MR  ──→  STOP  ──→  Human Review  │
│   (git-develop)       (git-submit)      ↑                       │
│                                         │                       │
│                            This skill stops here                │
│                            and reports the MR URL               │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow

### Step 1: Verify Branch State

Before submission, verify the work is ready:

```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "ERROR: Cannot submit from main/master. Must be on a feature branch."
    exit 1
fi
git status
```

Check that:
- Working on a feature branch (not main/master)
- All changes are committed (clean working directory)
- Branch name follows convention: `feature/`, `fix/`, or `hotfix/`

### Step 2: Run Code Review (Python Projects)

For Python projects, run automated code review before submission:

```bash
# Get changed Python files
CHANGED_PY_FILES=$(git diff --name-only main...HEAD --diff-filter=ACMR | grep '\.py$' || true)

if [ -n "$CHANGED_PY_FILES" ]; then
    # Run ruff linter
    uv run ruff check $CHANGED_PY_FILES
fi
```

**If ruff finds issues, STOP.** Report the issues and suggest fixes:
- Show the specific errors and file locations
- Suggest running `uv run ruff check --fix .` for auto-fixable issues
- Wait for developer to fix before continuing

**Only continue to Step 3 if ruff passes.**

### Step 3: Run Unit Tests (Fast Check)

Run **unit tests only** as a quick sanity check. Do NOT run UI/E2E tests—those are slow and should run in CI.

```bash
# Swift/iOS projects - unit tests only
make test-tks  # or swift test for SPM packages

# Python projects
pytest tests/unit/  # unit tests only, not integration/e2e

# JavaScript/TypeScript
npm run test:unit
```

**If unit tests fail, STOP.** Report the failures and wait for fixes.

**Note**: The developer explicitly requested submission, so trust their judgment. If you're unsure whether tests have been run, ask rather than running a long test suite.

### Step 4: Push to Remote

```bash
git push -u origin $(git branch --show-current)
```

If rejected due to upstream changes:
```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if needed, then:
git push -u origin $(git branch --show-current)
```

### Step 5: Detect Platform and Check for Existing MR/PR

First detect the platform:
```bash
PLATFORM=$(bash scripts/detect_git_platform.sh)
```

Before creating a new MR, check if one already exists for this branch:

**For GitHub:**
```bash
EXISTING=$(gh pr list --head $(git branch --show-current) --json url --jq '.[0].url')
if [ -n "$EXISTING" ]; then
    echo "✅ MR already exists: $EXISTING"
    gh pr view --web  # Open in browser, or just report URL
    # Skip to Step 7 (report) - do not attempt to create
fi
```

**For GitLab:**
```bash
EXISTING=$(glab mr list --source-branch $(git branch --show-current) 2>/dev/null | grep -v "^$")
if [ -n "$EXISTING" ]; then
    echo "✅ MR already exists for this branch"
    glab mr view  # Show existing MR details and URL
    # Skip to Step 7 (report) - do not attempt to create
fi
```

If an MR already exists, skip directly to Step 7 and report the existing URL. Do NOT attempt to create a duplicate.

### Step 6: Create MR/PR

Only if no existing MR was found, create one:

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

### Step 7: STOP and Report

**CRITICAL**: After creating (or finding existing) MR, STOP and report:

```
✅ Merge Request Created

Branch: feature/70-applies-condition-field
MR URL: https://gitlab.com/user/repo/-/merge_requests/42

The MR is now ready for human review.

Next steps (for humans):
1. Review the code changes
2. Run any additional manual testing
3. Approve and merge when satisfied
```

**DO NOT**:
- ❌ Auto-merge the MR
- ❌ Return to main branch
- ❌ Delete the feature branch
- ❌ Continue with any post-merge steps

The developer stays on the feature branch until the human decides to merge.

## What This Skill Does NOT Do

This skill deliberately excludes:
- ❌ **No auto-merge** - Human review must happen first
- ❌ **No return to main** - Stay on feature branch until human merges
- ❌ **No branch cleanup** - Human decides when to clean up
- ❌ **No "ship it" workflow** - That pattern was dangerous

## Workflow Decision Tree

```
User explicitly requests submission
    ↓
Verify on feature branch
    ↓ (fail if on main)
Check for uncommitted changes
    ↓ (warn and stop if dirty)
Run code review (Python: ruff check)
    ↓ (stop if linting errors)
Run unit tests (fast check only)
    ↓ (stop if tests fail)
Push branch to remote
    ↓ (handle rebase if needed)
Detect platform (GitHub/GitLab)
    ↓
Check for existing MR/PR
    ↓
    ├── MR exists → Report existing URL → STOP
    │
    └── No MR → Create MR/PR with proper format
                    ↓
              Report MR URL to user
                    ↓
                   STOP
                    ↓
          (Human reviews, approves, merges)
```

## Error Handling

| Situation | Action |
|-----------|--------|
| On main/master branch | STOP - cannot submit from main |
| Uncommitted changes | STOP - commit first (use git-develop) |
| Ruff linting fails | STOP - fix linting errors before submission |
| Unit tests fail | STOP - fix tests before submission |
| Push rejected | Attempt rebase; if conflicts, STOP and report |
| MR already exists | Report existing MR URL (no error, just skip creation) |
| MR creation fails | Report error (auth issue, permissions, etc.) |

## Quick Reference

### Submission Commands
```bash
# Check ready state
git status
git branch --show-current

# Push to remote
git push -u origin $(git branch --show-current)

# Detect platform
bash scripts/detect_git_platform.sh

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

### MR Title Format
```
<Type> #<issue>: <Brief description>
```

Examples:
- `Fix #70: Use applies_condition field instead of hardcoded checks`
- `Add #123: Party management debug commands`
- `Refactor #89: Extract condition system into separate module`

## Resources

### scripts/
- `detect_git_platform.sh` - Detects GitHub vs GitLab to use correct CLI tool (gh/glab)

### references/
- `pr_template.md` - Complete MR/PR format with real examples from projects
