---
name: submit
effort: medium
description: "Feature submission phase. Invoke with `/submit` or when user says 'ready for review', 'create PR', 'submit'. Pushes branch, creates PR/MR, handles review iteration, and gates to merge/deploy when approved."
---

# Feature Submission Phase

Submit completed work for review, iterate on feedback, and merge when approved.

## Usage

```
/submit
```

**Also triggers on:**
- "ready for review"
- "create PR" / "create MR"
- "submit for review"
- "push this"
- "open a pull request"

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  SUBMIT PHASE                                                   │
│                                                                 │
│   Push → Create PR → Review Loop → Gate → Merge → Cleanup      │
│                          ↑    │                                 │
│                          └────┘                                 │
│                      (iterate on feedback)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Steps

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
- Branch name uses one of the prefixes in `~/.claude/docs/source-control.md`:
  `feature/`, `fix/`, `bugfix/`, `hotfix/`, `chore/`, `docs/`, `test/`, `refactor/`

### Step 2: Run Code Review

Detect project domain using the detection script:

```bash
DOMAIN=$(bash skills/submit/scripts/detect_project_domain.sh)
echo "Detected domain: $DOMAIN"
```

Then invoke the reviewer matching the detected domain:

| Domain | Reviewer | Type |
|--------|----------|------|
| `swift` | `swift-swiftui-reviewer` | Agent (subagent_type) |
| `python` | `python-code-reviewer` | Skill |
| `cpp-qt` | `cpp-qt-reviewer` | Skill |
| `unknown` | STOP — ask user which reviewer to use |

**IMPORTANT:** Always run the detection script. Do NOT guess the domain from context.

**If critical issues found, STOP.** Report issues and wait for fixes.

### Step 3: Run Unit Tests

Quick sanity check before pushing. Run the project's test command (detected from project config or conventions).

**If tests fail, STOP.** Report failures and wait for fixes.

### Step 4: Push to Remote

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

### Step 5: Detect Platform and Check for Existing PR

```bash
PLATFORM=$(bash scripts/detect_git_platform.sh)
```

**GitHub:**
```bash
EXISTING=$(gh pr list --head $(git branch --show-current) --json url --jq '.[0].url')
if [ -n "$EXISTING" ]; then
    echo "PR exists: $EXISTING"
fi
```

**GitLab:**
```bash
EXISTING=$(glab mr list --source-branch $(git branch --show-current) 2>/dev/null | grep -v "^$")
```

If PR exists, skip to Step 7 (review loop).

### Step 6: Create PR/MR

**GitHub:**
```bash
gh pr create --title "<Type> #<issue>: <description>" --body "$(cat <<'EOF'
## Summary
- Bullet point 1
- Bullet point 2

## Changes
- **file1.py**: What changed and why

## Testing
- [x] Unit tests pass
- [x] Manual testing completed

## Related Issues
Fixes #<issue>
EOF
)"
```

**GitLab:**
```bash
glab mr create --title "<Type> #<issue>: <description>" --description "..."
```

### Step 7: Report PR and Enter Review Loop

```
✅ Pull Request Created (or exists)

Branch: feature/<issue>-<description>
PR URL: <url>

Awaiting human review. Let me know when:
- You have review feedback to address
- The review is approved and ready to merge
```

### Step 8: Review Iteration Loop

When user reports review feedback:

1. Read the feedback (user pastes or describes comments)
2. Make requested changes
3. Commit with message: `Update #<issue>: Address review feedback`
4. Push changes: `git push`
5. Report: "Changes pushed. PR updated."
6. Return to waiting for review outcome

### Step 9: Gate to Merge

When user confirms review is approved:

```
✅ Review approved!

Ready to merge and deploy?
- Yes → I'll merge the PR and clean up
- No → Keep PR open for now
```

### Step 10: Merge and Cleanup

If user confirms merge:

**GitHub:**
```bash
# Wait for CI if configured
gh pr checks

# Merge with squash
gh pr merge --squash --delete-branch
```

**GitLab:**
```bash
glab mr merge --squash --remove-source-branch
```

### Step 11: Return to Main

```bash
git checkout main
git pull origin main

# Delete local branch (remote already deleted by merge)
git branch -d <branch-name>
```

### Step 12: Report Success

```
✅ Merged and deployed!

Commit: <merged commit hash>
PR: <pr_number> (closed)
Branches cleaned up: ✓

You're now on main with latest changes.
```

## Error Handling

| Situation | Action |
|-----------|--------|
| On main/master branch | STOP - cannot submit from main |
| Uncommitted changes | STOP - commit first |
| Linting fails | STOP - fix before submission |
| Tests fail | STOP - fix before submission |
| Push rejected | Attempt rebase; if conflicts, STOP |
| PR already exists | Skip creation, enter review loop |
| Merge conflicts | STOP - ask user to resolve |
| CI checks failing | STOP - wait for fixes |

## Resources

### scripts/
- `detect_git_platform.sh` - Detects GitHub vs GitLab
- `detect_project_domain.sh` - Detects project domain for code reviewer selection

### references/
- `pr_template.md` - PR format examples

## Phase Complete

After merge, the feature loop is complete. User returns to main branch, ready for next `/spec` or `/implement`.
