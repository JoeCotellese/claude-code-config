---
name: submit
effort: medium
description: "Feature submission phase. Invoke with `/submit` or when user says 'ready for review', 'create PR', 'submit'. Confirms the Definition of Done passed, runs a fresh-context code review committee on fixed lenses sized by the effort label, pushes, creates the PR/MR, handles review iteration, and gates to merge."
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
│   Committee → Push → Create PR → Review Loop → Gate → Merge     │
│                                      ↑    │                     │
│                                      └────┘                     │
│                                 (iterate on feedback)           │
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

### Step 2: Confirm the Definition of Done Passed

Look for a `DOD VERDICT` line for this issue with `status=PASS` or `status=PASS-with-caveats`,
and the results file it names.

If there is none, run `/verify` before going further. Submitting work whose acceptance test was
never run puts the whole judgment on the reviewers, which is what the loop exists to avoid.

### Step 3: Run the Code Review Committee

Detect project domain using the detection script:

```bash
DOMAIN=$(bash ~/.claude/skills/submit/scripts/detect_project_domain.sh)
echo "Detected domain: $DOMAIN"
```

**IMPORTANT:** Always run the detection script. Do NOT guess the domain from context.

Reviewers run in **fresh contexts** via the Agent tool. The builder does not grade its own
work: an agent that watched the code get written has already accepted every assumption in it.
Give each one the diff, the issue, and one lens only.

**The lenses, in priority order:**

1. **Correctness against the acceptance criteria.** Read the ACs from the issue and the diff.
   Does the code do what each criterion says, including the empty and error paths? This lens
   does not care about style.
2. **Platform safety.** The domain-specific reviewer, which owns this lens:
   - `swift` → `swift-swiftui-reviewer` agent — concurrency and main-actor safety
   - `python` → `python-code-reviewer` skill
   - `cpp-qt` → `cpp-qt-reviewer` skill
   - `unknown` → STOP, ask the user which reviewer to use
3. **Test adequacy.** For each test added on this branch: would it still fail if the fix were
   reverted? A test that passes either way guards nothing. This lens also checks that every
   `[test: <name>]` acceptance criterion has the test it names.

**Size gating.** `/ready` recorded a committee tier in the issue from the `effort/` label. Use
it rather than re-deriving it:

- **effort/S** — lens 1 only.
- **effort/M** — lenses 1 and 2.
- **effort/L** — all three.

**Each reviewer returns a blocking finding count.** Only blocking findings stop the
submission. Non-blocking findings get logged to the issue and dropped — without that rule
every submission takes another round on somebody's style preference.

**If any lens returns a blocking finding, STOP.** Report and wait for fixes. A blocking finding
that reveals a gap the Definition of Ready should have caught is also a `/retro`.

### Step 4: Run Unit Tests

Re-run after the committee. `/verify` already ran the suite, but committee fixes landed since
then, so this catches what those fixes broke.

**If tests fail, STOP.** Report failures and wait for fixes.

### Step 5: Push to Remote

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

### Step 6: Detect Platform and Check for Existing PR

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

If PR exists, skip to Step 8 (review loop).

### Step 7: Create PR/MR

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
- [x] Definition of Done: PASS — <results file path>
- [x] Code review committee: <n> lenses, 0 blocking findings

## Related Issues
Fixes #<issue>
EOF
)"
```

**GitLab:**
```bash
glab mr create --title "<Type> #<issue>: <description>" --description "..."
```

### Step 8: Report PR and Enter Review Loop

```
✅ Pull Request Created (or exists)

Branch: feature/<issue>-<description>
PR URL: <url>

Awaiting human review. Let me know when:
- You have review feedback to address
- The review is approved and ready to merge
```

### Step 9: Review Iteration Loop

When user reports review feedback:

1. Read the feedback (user pastes or describes comments)
2. Make requested changes
3. Commit with message: `Update #<issue>: Address review feedback`
4. Push changes: `git push`
5. Report: "Changes pushed. PR updated."
6. Return to waiting for review outcome

### Step 10: Gate to Merge

When user confirms review is approved:

```
✅ Review approved!

Ready to merge and deploy?
- Yes → I'll merge the PR and clean up
- No → Keep PR open for now
```

### Step 11: Merge and Cleanup

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

### Step 12: Return to Main

```bash
git checkout main
git pull origin main

# Delete local branch (remote already deleted by merge)
git branch -d <branch-name>
```

### Step 13: Report Success

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
| No `DOD VERDICT` for the issue | Run `/verify` before submitting |
| Blocking committee finding | STOP - fix, then re-run that lens only |
| Blocking finding the DoR should have caught | Fix it, then `/retro` the gate |

## Resources

### scripts/
- `detect_git_platform.sh` - Detects GitHub vs GitLab
- `detect_project_domain.sh` - Detects project domain for code reviewer selection

### references/
- `pr_template.md` - PR format examples

## Phase Complete

After merge, the feature loop is complete. User returns to main branch, ready for next `/spec` or `/implement`.
