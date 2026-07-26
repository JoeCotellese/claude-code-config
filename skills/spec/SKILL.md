---
name: spec
effort: xhigh
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
Step 1-3:  PM → UX           (automatic)
Step 4:    GATE              ← "Ready for architecture?"
Step 5:    Arch              (automatic)
Step 6:    Sizing            (automatic)
Step 7-9:  Issue creation    (automatic)
Step 10:   GATE              ← "Ready to implement?"
```

## Workflow Steps

Execute these steps sequentially. Steps flow automatically EXCEPT at gates (Steps 4 and 10) where you MUST stop and ask the user.

### Step 1: Detect Project Domain

Analyze the codebase to determine the primary technology:

```bash
# Check for Swift/iOS project
if ls *.xcodeproj >/dev/null 2>&1 || ls *.xcworkspace >/dev/null 2>&1; then
    DOMAIN="swift"
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

**After architecture is complete, AUTOMATICALLY proceed to sizing.**

### Step 6: Value/Effort Sizing

Assess the feature on two dimensions using the labels available in the repo. Use AskUserQuestion to confirm sizing with the user.

**Value** — business impact to users or the product:
| Rating | Meaning |
|--------|---------|
| S | Nice-to-have, minor polish |
| M | Useful improvement, affects some users |
| L | Important feature, clear user demand |
| XL | Critical capability, blocks major goals |

**Effort** — implementation complexity:
| Rating | Meaning |
|--------|---------|
| S | 1-2 files, clear scope, < 1 hour |
| M | Multiple files, some investigation needed |
| L | Cross-cutting, multi-service, needs design |
| XL | Epic-level, should be broken into sub-issues |

Present the proposed sizing to the user with brief rationale for each. Use the AskUserQuestion tool:
```
Based on the requirements and architecture:

**Value: <proposed>** — <one-line rationale>
**Effort: <proposed>** — <one-line rationale>

Does this sizing look right?
- Yes
- Adjust value
- Adjust effort
- Adjust both
```

**Collect confirmed sizing as:** `VALUE_SIZE`, `EFFORT_SIZE`, `VALUE_RATIONALE`, `EFFORT_RATIONALE`

**Then AUTOMATICALLY proceed to create the issue.**

### Step 7: Detect Git Platform

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

### Step 8: Create Issue

Compose the issue from collected outputs, using the template in `assets/issue-template.md`.

**For GitHub:**
```bash
gh issue create \
  --title "Feature: <brief title from feature description>" \
  --label "value/<VALUE_SIZE>" \
  --label "effort/<EFFORT_SIZE>" \
  --body "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For GitLab:**
```bash
glab issue create \
  --title "Feature: <brief title from feature description>" \
  --label "value/<VALUE_SIZE>" \
  --label "effort/<EFFORT_SIZE>" \
  --description "$(cat <<'EOF'
<composed issue body>
EOF
)"
```

**For unknown platform:** Output the composed issue to the user for manual creation, noting the recommended labels.

### Step 9: Report Success

Return to user:
- Issue URL (if created)
- Issue number (e.g., #123)
- Summary of what was planned
- Value/Effort sizing applied

**Then IMMEDIATELY proceed to Step 10 (the final gate).**

### Step 10: GATE - Ready for Next Phase

**CRITICAL**: STOP and ask user before proceeding.

**Does this feature have a UI?** If yes, the next phase is `/ui-design` (UI-first: an
approved static prototype before backend work). If it's backend/CLI-only, the next phase is
`/implement` directly. When the feature has a UI, mark the issue's UX and acceptance
sections **provisional — pending design**, since `/ui-design` will finalize them.

Use the AskUserQuestion tool to prompt (UI feature):
```
✅ Spec complete!

Issue: #<issue_number>
URL: <issue_url>

This feature has a UI — next is the design phase (static prototype before backend).
- Yes → Continue to /ui-design #<issue_number>
- Refine spec → Let's adjust before designing
- Stop here → I'll pick it up later
```

For a backend/CLI-only feature, swap the handoff to `/implement #<issue_number>` instead.

**DO NOT invoke the next phase until the user explicitly confirms "Yes".**

**When user confirms "Yes":** Invoke the next skill using the Skill tool:
```
Skill tool: skill="ui-design", args="#<issue_number>"      # UI feature
Skill tool: skill="implement", args="#<issue_number>"      # backend/CLI-only
```

This hands off to the next phase with the issue context.

## Output Composition

The issue should be scannable with clear sections:
1. **Overview** - One paragraph summary
2. **User Stories** - From PM phase
3. **UX Design** - From designer phase
4. **Architecture** - From architect phase
5. **Acceptance Criteria** - Consolidated checklist
6. **Analytics Events** - From PM phase
7. **Sizing** - Value/Effort ratings with rationale

## Error Handling

- **No git remote:** Output issue content for manual creation
- **CLI not authenticated:** Provide `gh auth login` or `glab auth login` instructions
- **Domain unknown:** Ask user to specify or provide generic architecture
- **Skill unavailable:** Skip that phase with a note, continue with available phases

## Dependencies

This skill orchestrates:
- `product-manager` skill (for PM phase)
- `ux-designer` skill (for design phase)
- `swift-architect`, `cpp-qt-architect`, or `python-architect` skill (for architecture)
- `gh` CLI (for GitHub issues)
- `glab` CLI (for GitLab issues)

## Next Phase

After spec is complete and user confirms, chains to → `/ui-design` (UI features) or
`/implement` (backend/CLI-only).
