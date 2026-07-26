---
name: implement
effort: xhigh
description: "Feature implementation phase. Invoke with `/implement #<issue>` or when user says 'implement', 'work on issue #', 'start coding'. Clears context, fetches issue, enters plan mode, then implements with TDD. Gates to /submit when complete."
---

# Feature Implementation Phase

Guide the development process from issue to tested, reviewable code.

## Usage

```
/implement #<issue_number>
/implement <issue_number>
```

**Example:**
```
/implement #123
```

**Also triggers on:**
- "implement #123"
- "work on issue #123"
- "let's work on #123"
- "start coding #123"

## Workflow Overview

```
Step 1: Clear context (fresh start)
Step 2: Fetch issue content
Step 3: Create feature branch
Step 4: Enter plan mode → write implementation plan
Step 5: GATE              ← "Plan approved?"
Step 6: Implement (TDD)
Step 7: QA (tests + code review)
Step 8: GATE              ← "Ready for review?"
```

## Workflow Steps

### Step 1: Clear Context

Start fresh to avoid context pollution from the spec phase.

**Suggest to user:**
```
Starting implementation for #<issue_number>.
Recommend clearing context for a fresh start: /clear

Or we can continue in this session if you prefer.
```

If user agrees, they run `/clear` and re-invoke `/implement #<issue_number>`.
If user prefers to continue, proceed to Step 2.

### Step 2: Fetch Issue Content

Retrieve the issue to understand requirements:

**GitHub:**
```bash
gh issue view $ISSUE_NUM --json title,body,labels
```

**GitLab:**
```bash
glab issue view $ISSUE_NUM
```

Parse and extract:
- **Requirements** (from PM phase)
- **Architecture decisions** (from architect phase)
- **Acceptance criteria** (checklist)
- **UX constraints** (from designer phase)

### Step 3: Create Feature Branch

Check if branch already exists:

```bash
ISSUE_NUM="$1"
EXISTING_BRANCH=$(git branch -a | grep -E "(feature|fix|hotfix)/${ISSUE_NUM}-" | head -1 | xargs)

if [ -n "$EXISTING_BRANCH" ]; then
    git checkout "$EXISTING_BRANCH"
    echo "Switched to existing branch: $EXISTING_BRANCH"
else
    bash scripts/create_feature_branch.sh $ISSUE_NUM feature <brief-description>
fi
```

### Step 4: Enter Plan Mode

**CRITICAL**: Enter plan mode to create an implementation plan before writing code.

Use the **EnterPlanMode** tool, then:
1. If implementing a Django feature, read `~/.claude/docs/django.md` for design principles to align against
2. Explore the codebase based on architecture from the issue
3. **Check for an inherited prototype.** If `/ui-design` ran, the feature branch already holds the approved target template rendered with a fake context (plus a throwaway `ponytail:` prototype view). Treat that template as the UI starting point — **do not rebuild it**; the plan wires it to real services and removes/repurposes the throwaway route.
4. Identify files to create/modify
5. Map each task to its TDD cycle (failing test → minimal code → refactor)
6. Write a step-by-step implementation plan

**Plan should include:**
- Files to create/modify (with full paths)
- Order of implementation (dependencies first)
- For each task: the test to write first, then the implementation
- Key code patterns to follow from existing codebase
- Acceptance criteria mapped to implementation tasks

**TDD is the default.** Every task in the plan should specify what test gets written first. If any task genuinely cannot be test-driven (e.g., pure UI layout, config-only changes, infrastructure wiring), it MUST be explicitly marked in the plan with a reason. These exceptions will be flagged to the user at the plan approval gate.

Write the plan to the plan file (path provided by plan mode).

### Step 5: GATE - Plan Approved

Use **ExitPlanMode** to present the plan for user approval.

**DO NOT write any code until user approves the plan.**

If user requests changes → update the plan and re-present.
If user approves → proceed to Step 6.

### Step 6: Implementation Loop

Execute the approved plan using TDD:

1. Write a failing test for the first task
2. Run the test — confirm it fails
3. Implement the minimal code to make it pass
4. Run the test — confirm it passes
5. Refactor if needed
6. Commit (test and implementation together)
7. Repeat for the next task

**TDD Exception Gate:** If you encounter a task where TDD is not feasible and it was not already flagged in the plan, you MUST stop and use **AskUserQuestion** before proceeding:

```
⚠️ TDD Exception

Task: <description of the task>
Reason TDD isn't feasible: <explanation>
Proposed approach: <tests-after / manual verification / etc.>

Proceed without TDD for this task?
- Yes → Continue with proposed approach
- No → Let's discuss an alternative
```

**Do NOT silently skip TDD.** Writing all tests at the end is not acceptable without explicit human acknowledgment.

**Commit format:**
```bash
git commit -m "$(cat <<'EOF'
<Type> #<issue>: <Brief description>

<Why explanation>
EOF
)"
```

**Commit types:** Fix, Add, Update, Refactor, Remove, Docs, Test, Chore

### Step 7: QA

**Run tests:**
```bash
# Swift/iOS
swift test

# Python
pytest

# React Native
npm run test
```

**Run code reviewer:**

| Domain | Reviewer |
|--------|----------|
| Swift | `swift-swiftui-reviewer` agent |
| Python | `python-code-reviewer` skill |

**TDD compliance check:**
Review the commit history for this branch. Tests should appear in commits *alongside* their implementation code, not lumped together at the end. If all tests were written after all implementation, flag this to the user — TDD was not followed.

**Manual QA (if needed):**
- Build and run the app
- Test the feature manually
- Verify acceptance criteria from the issue

Address any issues before proceeding.

### Step 8: GATE - Ready for Review

**CRITICAL**: STOP and ask user before proceeding to submit phase.

Use AskUserQuestion:
```
✅ Implementation complete!

Branch: feature/<issue>-<description>
Commits: <count> commits
Tests: ✓ passing
Code review: ✓ no critical issues

Ready for code review?
- Yes → Continue to /submit
- No → Continue working or run more tests
```

**When user confirms "Yes":** Invoke the `submit` skill:
```
Skill tool: skill="submit"
```

## Commit Quality Standards

Every commit MUST:
1. Start with a type prefix (Fix, Add, Update, etc.)
2. Reference the issue number (#123)
3. Have subject under 72 characters
4. Explain "why" in the body (not just "what")

See `references/commit_message_format.md` for examples.

## Git Hooks

Install hooks to enforce standards (once per repo):

```bash
bash scripts/setup_git_hooks.sh
```

## Error Handling

| Situation | Action |
|-----------|--------|
| Issue not found | Ask user for correct issue number |
| Branch conflict | Ask user how to resolve |
| Tests failing | Fix before gating to submit |
| Code review issues | Fix before proceeding |

## Resources

### scripts/
- `create_feature_branch.sh` - Creates properly named branches
- `pre_commit_hook.sh` - Blocks commits to main/master
- `commit_msg_hook.sh` - Validates commit message format
- `setup_git_hooks.sh` - Installs all git hooks

### references/
- `commit_message_format.md` - Commit message guidelines and examples

## Next Phase

After implementation is complete and user confirms, chains to → `/submit`
