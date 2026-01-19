---
name: workflow-plan
description: "User-invoked slash command for feature planning. Invoke with `/workflow:plan <feature description>`. Orchestrates product management, UX design, and architecture planning into a single GitHub/GitLab issue. Detects project domain (Swift, Python, React Native) and calls appropriate specialists."
---

# Feature Planning Workflow

Orchestrate a complete feature planning pipeline that produces a comprehensive issue ready for implementation.

## Usage

```
/workflow:plan <brief feature description>
```

**Example:**
```
/workflow:plan Add a recipe sharing feature with social integration
```

## Workflow Steps

Execute these steps sequentially, collecting output from each phase.

### Step 1: Detect Project Domain

Analyze the codebase to determine the primary technology:

```bash
# Check for Swift/iOS project
if ls *.xcodeproj >/dev/null 2>&1 || ls *.xcworkspace >/dev/null 2>&1; then
    DOMAIN="swift"
# Check for React Native
elif [ -f "package.json" ] && grep -q "react-native" package.json 2>/dev/null; then
    DOMAIN="react-native"
# Check for Python
elif ls *.py >/dev/null 2>&1 || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    DOMAIN="python"
else
    DOMAIN="unknown"
fi
echo "$DOMAIN"
```

Store the result for architect selection in Step 4.

### Step 2: Product Requirements (PM Phase)

Invoke the `product-manager-apple` skill to define requirements.

**Prompt the skill with:**
```
Define product requirements for: <user's feature description>

Focus on:
- User stories with acceptance criteria
- Success metrics and analytics events
- Accessibility requirements (tier level)
- Edge cases and error states

Output format: Feature brief (not full PRD unless complex)
```

**Collect output as:** `PM_OUTPUT`

### Step 3: UX Design (Designer Phase)

Use the Task tool to invoke the `apple-ux-designer` agent.

**Prompt:**
```
Review and provide UX guidance for this feature:

<user's feature description>

Context from PM:
<PM_OUTPUT summary - key user flows only>

Provide:
- HIG compliance considerations
- Navigation and interaction patterns
- Accessibility UX requirements
- Visual hierarchy recommendations
```

**Collect output as:** `UX_OUTPUT`

### Step 4: Architecture (Architect Phase)

Select architect based on DOMAIN from Step 1:

| Domain | Architect |
|--------|-----------|
| swift | Invoke `swift-architect` skill |
| react-native | Task agent: `react-native-architect` |
| python | Provide architecture inline (no dedicated skill) |
| unknown | Ask user to specify, or provide generic guidance |

**Prompt the architect with:**
```
Design architecture for: <user's feature description>

PM Requirements:
<PM_OUTPUT summary>

UX Constraints:
<UX_OUTPUT summary>

Provide:
- Component diagram (ASCII)
- Data flow
- File structure
- Key implementation decisions
```

**Collect output as:** `ARCH_OUTPUT`

### Step 5: Detect Git Platform

```bash
# From git-workflow skill
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$REMOTE_URL" | grep -qi "github"; then
    PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qi "gitlab"; then
    PLATFORM="gitlab"
else
    PLATFORM="unknown"
fi
echo "$PLATFORM"
```

### Step 6: Create Issue

Compose the issue from collected outputs using `assets/issue-template.md`.

**For GitHub:**
```bash
gh issue create \
  --title "Feature: <brief title from feature description>" \
  --body "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For GitLab:**
```bash
glab issue create \
  --title "Feature: <brief title from feature description>" \
  --description "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For unknown platform:** Output the composed issue to the user for manual creation.

### Step 7: Report Success

Return to user:
- Issue URL (if created)
- Summary of what was planned
- Suggested next steps (e.g., "Ready to start implementation with `/git-workflow`")

## Output Composition

Use the template in `assets/issue-template.md` to structure the final issue.

The issue should be scannable with clear sections:
1. **Overview** - One paragraph summary
2. **User Stories** - From PM phase
3. **UX Design** - From designer phase
4. **Architecture** - From architect phase
5. **Acceptance Criteria** - Consolidated checklist
6. **Analytics Events** - From PM phase

## Error Handling

- **No git remote:** Output issue content for manual creation
- **CLI not authenticated:** Provide `gh auth login` or `glab auth login` instructions
- **Domain unknown:** Ask user to specify or provide generic architecture
- **Skill/agent unavailable:** Skip that phase with a note, continue with available phases

## Dependencies

This skill orchestrates:
- `product-manager-apple` skill (for PM phase)
- `apple-ux-designer` Task agent (for design phase)
- `swift-architect` skill OR `react-native-architect` agent (for architecture)
- `gh` CLI (for GitHub issues)
- `glab` CLI (for GitLab issues)
