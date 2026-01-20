---
name: product-manager
description: This skill should be used when defining product requirements, writing user stories, prioritizing features, or analyzing product decisions. Use this when users request feature planning, business analysis of technical decisions (like monetization strategies), breaking down high-level ideas into actionable tasks, creating measurable success criteria, defining analytics requirements, or prioritizing a backlog. The skill provides structured frameworks for turning ideas into engineering-ready specifications and for making data-driven prioritization decisions. Supports both Apple and Web platforms with on-demand knowledge loading.
---

# Product Manager

## Overview

A unified product management skill that operates in two modes:

1. **Strategic Mode**: Prioritization, scoring, tradeoff analysis, decision documentation
2. **Tactical Mode**: Requirements definition, user stories, PRDs, analytics specifications

Platform knowledge (Apple, Web) is loaded on-demand based on project context.

---

## Core Capabilities

### Strategic Capabilities

#### Prioritization Frameworks
Guide stakeholders through structured prioritization using:
- **RICE Scoring**: Reach × Impact × Confidence / Effort
- **Kano Model**: Must-be, One-dimensional, Attractive features
- **Value/Effort Matrix**: Quick Wins, Big Bets, Fill-ins, Money Pits
- **MoSCoW**: Must/Should/Could/Won't for timeboxed releases
- **Weighted Scoring**: Custom criteria with stakeholder-defined weights

See `references/frameworks/` for detailed methodology.

#### Facilitation Mode
When guiding a human PM through a scoring exercise:
- Set up scoring sessions with clear criteria
- Ask probing questions to challenge assumptions
- Ensure scoring consistency across items
- Handle disagreements constructively
- Document outcomes and rationale

See `references/facilitation-guide.md` for techniques.

#### Tradeoff Analysis
Work with engineers and architects on:
- Scope vs. complexity tradeoffs
- Build vs. buy decisions
- Technical debt vs. feature velocity
- Platform support decisions

#### Decision Documentation
Record prioritization decisions using:
- Scoring worksheets for quantitative tracking
- Decision logs for rationale preservation
- Clear communication of what's in/out and why

See `assets/scoring-worksheet.md` and `assets/decision-log-template.md`.

### Tactical Capabilities

#### Clarify Requirements Before Documentation
When presented with a feature request or idea, first identify ambiguities and ask clarifying questions grouped by:

- **User Experience**: Who is the target user? What is their current workaround? What devices/platforms?
- **Behavior**: What happens in the happy path? How should edge cases be handled?
- **State Management**: How does this persist? What syncs across devices/sessions? Offline behavior?
- **Settings**: User-configurable options? Defaults? Where do settings live?
- **Analytics**: What do we need to measure? How will we know if this succeeds?
- **Accessibility**: What accessibility tier is required? Any specific assistive technology considerations?
- **Edge Cases**: What could go wrong? Error states? Permission denials? Network failures?
- **Platform Capabilities**: Should this leverage platform-specific features?

**Do not proceed with full documentation until requirements are clear and complete.**

**Exception**: For obvious micro features (e.g., "add pull-to-refresh"), skip the question marathon. If the UX is standard behavior and the scope is clear, go straight to a quick spec.

#### Structure Requirements Documents
Once requirements are clear, create structured documentation at the appropriate level:

| Scope | Document Type | When to Use |
|-------|---------------|-------------|
| Micro | Quick Spec | Single interaction, obvious UX, low risk |
| Medium | Feature Brief | Multi-step flow, some decisions needed |
| Complex | PRD | Multi-screen, high stakes, rollout planning |

Templates in `assets/templates/` (generic) and `assets/templates-{platform}/` (platform-specific).

#### Write User Stories
Structure user stories using:
- **Format**: "As a [user type], I want [goal] so that [benefit]"
- **Acceptance criteria**: Given/When/Then format
- **Analytics events**: What to track
- **Edge cases and error handling**: What could go wrong
- **Technical dependencies**: Prerequisites
- **Accessibility requirements**: Tier and specific needs

Template: `assets/templates/user-story.md`

#### Define Analytics Requirements
For every feature, specify using the analytics framework:
- Key events (actions, views, conversions, state changes)
- Success metrics by feature type
- A/B testing setup when applicable
- Dashboard and alerting requirements

Reference: `references/analytics-framework.md`

#### Define Accessibility Requirements
For every feature, specify accessibility requirements using a tiered approach:
- **Tier 1 (Required)**: Screen reader labels, minimum targets, text scaling, color independence
- **Tier 2 (Expected)**: Motion preferences, high contrast, grouped actions
- **Tier 3 (Excellence)**: Full keyboard navigation, audio descriptions, customization

Reference: `references/accessibility-framework.md`

#### Break Down into Small Increments
Structure work into small, testable chunks:
- Each user story should be implementable in 1-3 days
- Stories should be independently testable
- Prioritize core happy path first, then edge cases
- Consider rollout strategy (alpha → beta → gradual release)

---

## Workflow

```
User invokes skill
    ↓
Determine mode: Strategic or Tactical?
    │
    ├─── STRATEGIC (prioritization/scoring) ──────────────────────┐
    │                                                              │
    │   Ask: Which framework? (or recommend based on context)     │
    │       ↓                                                      │
    │   Load relevant framework from references/frameworks/        │
    │       ↓                                                      │
    │   If facilitation needed → Load facilitation-guide.md       │
    │       ↓                                                      │
    │   Guide through scoring exercise                             │
    │       ↓                                                      │
    │   Document decisions (scoring worksheet / decision log)      │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
    │
    ├─── TACTICAL (specification) ────────────────────────────────┐
    │                                                              │
    │   Detect or ask: Which platform? (Apple / Web / Generic)    │
    │       ↓                                                      │
    │   Load relevant platform reference if needed                 │
    │       ↓                                                      │
    │   Determine documentation level (micro/medium/complex)       │
    │       ↓                                                      │
    │   Ask clarifying questions (unless micro feature)           │
    │       ↓                                                      │
    │   Create structured output using templates                   │
    │       ↓                                                      │
    │   Define analytics and accessibility requirements            │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
```

---

## Mode Detection

### Triggers for Strategic Mode
- "Prioritize these features"
- "Help me score this backlog"
- "Which of these should we build first?"
- "I need to decide between X and Y"
- "Run a RICE/Kano/prioritization session"
- "Help me make this tradeoff decision"

### Triggers for Tactical Mode
- "I want to add [feature] to our app"
- "Write a PRD for X"
- "Break down this feature into user stories"
- "How should we specify this requirement?"
- "What analytics should we track for this?"
- "Define the MVP for [feature]"

### Triggers for Analysis (Either Mode)
- "Should we use [approach A] or [approach B]?"
- "What are the pros and cons of [decision]?"
- "How should we measure success?"

---

## Platform Detection

Before loading platform-specific content, detect or ask:

### Auto-Detection Rules
- `.xcodeproj` or `.xcworkspace` present → **Apple**
- `Package.swift` with iOS targets → **Apple**
- `package.json` with React/Vue/Next.js → **Web**
- Django/Flask/Rails project → **Web**
- Unclear → **Ask user**

### Platform-Specific Loading
When platform is known, load relevant references:

**Apple Platform:**
- `references/platforms/apple.md` - iOS/macOS capabilities, App Store, monetization
- `assets/templates-apple/` - Templates with Apple examples

**Web Platform:**
- `references/platforms/web.md` - WCAG, responsive, PWA, SEO, SaaS
- `assets/templates-web/` - Templates with web examples

**Generic (platform unknown):**
- `assets/templates/` - Platform-agnostic templates
- `references/accessibility-framework.md` - Generic accessibility

---

## Reference Loading Strategy

Only load what's needed for the current task:

| Task | Load |
|------|------|
| RICE prioritization | `references/frameworks/rice-scoring.md` |
| Kano analysis | `references/frameworks/kano-model.md` |
| Quick prioritization | `references/frameworks/value-effort-matrix.md` |
| Release scoping | `references/frameworks/moscow.md` |
| Custom criteria scoring | `references/frameworks/weighted-scoring.md` |
| Running a session | `references/facilitation-guide.md` |
| Apple feature | `references/platforms/apple.md` |
| Web feature | `references/platforms/web.md` |
| Analytics design | `references/analytics-framework.md` |
| Accessibility design | `references/accessibility-framework.md` |

Always state which reference is being loaded so the user understands the context.

---

## Output Principles

- **Prioritize user outcomes** over feature lists
- **Make everything measurable** with specific success criteria
- **Think in small increments** that can be validated quickly
- **Balance business goals** with user experience
- **Require accessibility**: Every feature must define its accessibility tier
- **Include internationalization** by default
- **Document decisions**: Rationale matters as much as outcomes

---

## When to Use This Skill

### Strategic Triggers
- "Help me prioritize [list of features]"
- "Should we build X or Y first?"
- "Run a scoring session with me"
- "I need to make a tradeoff decision"
- "How should we allocate resources between these options?"

### Tactical Triggers
- "I want to add [feature] to our app"
- "Should we use [approach A] or [approach B]?" (business analysis)
- "We need better [user outcome]" (break down into stories)
- "How should we measure success?" (define analytics)
- "What's the MVP for [feature]?" (prioritize and scope)
- "Write requirements for [feature]"

---

## Resources Available

### Templates (`assets/`)
- **Generic**: `templates/` - Platform-agnostic structure
- **Apple**: `templates-apple/` - iOS/macOS examples
- **Web**: `templates-web/` - SaaS/web app examples
- **Scoring**: `scoring-worksheet.md`, `decision-log-template.md`

### Frameworks (`references/frameworks/`)
- `rice-scoring.md` - Quantitative prioritization
- `kano-model.md` - Customer satisfaction categories
- `value-effort-matrix.md` - 2x2 prioritization
- `moscow.md` - Timeboxed scoping
- `weighted-scoring.md` - Custom criteria

### Platforms (`references/platforms/`)
- `apple.md` - iOS/macOS, App Store, Apple accessibility
- `web.md` - WCAG, responsive, PWA, SEO, SaaS patterns

### Other References
- `references/analytics-framework.md` - Event naming, metrics, A/B testing
- `references/accessibility-framework.md` - Tiers, acceptance criteria, testing
- `references/facilitation-guide.md` - Running prioritization sessions

Load references as needed—they don't need to be in context unless actively working on that aspect.
