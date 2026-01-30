---
name: spec
description: "Feature specification phase. Invoke with `/spec <feature description>` or when user says 'new feature', 'plan feature', 'create spec'. Orchestrates product management, UX design, and architecture planning into a single GitHub/GitLab issue. Gates to /implement when complete."
---

# Feature Specification Phase

Orchestrate a complete feature planning pipeline that produces a comprehensive issue ready for implementation.

## Usage

```
/spec <brief feature description>
```

**Example:**
```
/spec Add a recipe sharing feature with social integration
```

**Also triggers on:**
- "new feature X"
- "plan feature X"
- "create spec for X"
- "I have an idea for X"

## Workflow Overview

```
Step 1-3: PM → UX           (automatic)
Step 4:   GATE              ← "Ready for architecture?"
Step 5-8: Arch → Issue      (automatic)
Step 9:   GATE              ← "Ready to implement?"
```

## Workflow Steps

Execute these steps sequentially. Steps flow automatically EXCEPT at gates (Steps 4 and 9) where you MUST stop and ask the user.

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

Invoke the `product-manager` skill to define requirements.

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

Invoke the `ux-designer` skill.

**Prompt:**
```
Review and provide UX guidance for this feature:

<user's feature description>

Context from PM:
<PM_OUTPUT summary - key user flows only>

Provide:
- Platform-specific design guidelines compliance
- Navigation and interaction patterns
- Accessibility UX requirements
- Visual hierarchy recommendations
```

**Collect output as:** `UX_OUTPUT`

### Step 4: GATE - Review Requirements & UX

**CRITICAL**: STOP and ask user before proceeding to architecture.

Use the AskUserQuestion tool to prompt:
```
Requirements and UX design complete.

**PM Requirements:** <brief summary>
**UX Guidance:** <brief summary>

Ready to proceed to architecture design?
- Yes → Continue to architecture phase
- Refine requirements → Let's adjust the PM requirements
- Refine UX → Let's adjust the UX design
```

**DO NOT continue to architecture until user explicitly confirms.**

### Step 5: Architecture (Architect Phase)

Select architect based on DOMAIN from Step 1 (detected earlier):

| Domain | Architect |
|--------|-----------|
| swift | Invoke `swift-architect` skill |
| react-native | Invoke `react-native-architect` skill |
| python | Invoke `python-architect` skill |
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

**After architecture is complete, AUTOMATICALLY proceed to create the issue. No gate here.**

### Step 6: Detect Git Platform

```bash
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

### Step 7: Create Issue

Compose the issue from collected outputs.

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

### Step 8: Report Success

Return to user:
- Issue URL (if created)
- Issue number (e.g., #123)
- Summary of what was planned

**Then IMMEDIATELY proceed to Step 9 (the final gate).**

### Step 9: GATE - Ready to Implement

**CRITICAL**: STOP and ask user before proceeding to implementation phase.

Use the AskUserQuestion tool to prompt:
```
✅ Spec complete!

Issue: #<issue_number>
URL: <issue_url>

Ready to start implementation?
- Yes → Continue to /implement #<issue_number>
- Refine spec → Let's adjust before implementing
- Stop here → I'll implement later
```

**DO NOT invoke /implement until user explicitly confirms "Yes".**

**When user confirms "Yes":** Invoke the `implement` skill using the Skill tool:
```
Skill tool: skill="implement", args="#<issue_number>"
```

This hands off to the implementation phase with the issue context.

## Output Composition

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
- **Skill unavailable:** Skip that phase with a note, continue with available phases

## Dependencies

This skill orchestrates:
- `product-manager` skill (for PM phase)
- `ux-designer` skill (for design phase)
- `swift-architect`, `react-native-architect`, or `python-architect` skill (for architecture)
- `gh` CLI (for GitHub issues)
- `glab` CLI (for GitLab issues)

## Next Phase

After spec is complete and user confirms, chains to → `/implement`
