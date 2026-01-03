---
name: product-manager-apple
description: This skill should be used when defining product requirements, writing user stories, or analyzing features from a business perspective for Apple platforms. Use this when users request feature planning, business analysis of technical decisions (like monetization strategies), breaking down high-level ideas into actionable tasks, creating measurable success criteria, or defining analytics requirements. The skill provides structured frameworks for turning ideas into engineering-ready specifications with Apple platform considerations.
---

# Product Manager - Apple Platforms

## Overview

Transform feature ideas into engineering-ready specifications for Apple platforms (iOS, iPadOS, macOS, watchOS, tvOS). Provide structured product management workflows that define requirements, write user stories, establish analytics tracking, and ensure business value alignment.

## Core Capabilities

### 1. Clarify Requirements Before Documentation

When presented with a feature request or idea, first identify ambiguities and ask clarifying questions grouped by:

- **User Experience**: Who is the target user? What is their current workaround? What devices/platforms?
- **Behavior**: What happens in the happy path? How should edge cases be handled?
- **State Management**: How does this persist? What syncs across devices? Offline behavior?
- **Settings**: User-configurable options? Defaults? Where do settings live?
- **Analytics**: What do we need to measure? How will we know if this succeeds?
- **Accessibility**: What accessibility tier is required? Any specific assistive technology considerations?
- **Edge Cases**: What could go wrong? Error states? Permission denials? Network failures?
- **Platform Capabilities**: Should this use widgets? Shortcuts? Live Activities? iCloud sync?

**Do not proceed with full documentation until requirements are clear and complete.**

**Exception**: For obvious micro features (e.g., "add pull-to-refresh"), skip the question marathon. If the UX is standard iOS behavior and the scope is clear, go straight to a quick spec.

### 2. Structure Requirements Documents

Once requirements are clear, create structured documentation at the appropriate level:

#### For Micro Features: Use Quick Spec
- Single-interaction, obvious UX, low risk
- 5-10 lines covering what, why, acceptance criteria, analytics
- Lives in the issue/ticket itself — no separate doc needed
- **Location**: `assets/quick-spec-template.md`

#### For Medium Features: Use Feature Brief
- Multi-step flow, some decisions needed
- One-page summary with user flow and success metrics
- Technical notes and analytics events
- **Location**: `assets/feature-brief-template.md`

#### For Complex Features: Use PRD Template
- Multi-screen, high stakes, needs rollout planning
- Executive summary with business justification
- Detailed user stories with acceptance criteria
- Analytics implementation plan and risk assessment
- **Location**: `assets/prd-template.md`

### 3. Write User Stories

Structure user stories using the provided template:

**Format**: "As a [user type], I want [goal] so that [benefit]"

**Include**:
- Acceptance criteria (Given/When/Then format)
- Analytics events to track
- Edge cases and error handling
- Technical dependencies
- Platform-specific considerations (accessibility, localization, privacy)

**Reference**: `assets/user-story-template.md` for complete structure and examples

### 4. Define Analytics Requirements

For every feature, specify using the analytics framework:

- **Key events**: User actions, screen views, conversions, state changes
- **Success metrics**: Choose appropriate metrics based on feature type (engagement, retention, monetization, content, social)
- **A/B testing**: Hypothesis, variants, primary metric, success criteria (when applicable)
- **Dashboard requirements**: Real-time monitoring, daily reports, alerts

**Reference**: `references/analytics-framework.md` for detailed event naming, metrics by feature type, and Apple privacy considerations

### 5. Consider Apple Platform Constraints

Evaluate Apple-specific factors:

- **Platform capabilities**: Widgets, Live Activities, Shortcuts, iCloud, ecosystem integration
- **App Store guidelines**: Common rejection reasons, business model constraints
- **Monetization**: IAP vs subscription tradeoffs, pricing strategies
- **Version support**: iOS version strategy, device compatibility
- **Localization**: Priority markets, regional requirements
- **Compliance**: Privacy (ATT, GDPR, COPPA), regional laws

**Reference**: `references/apple-platform-considerations.md` for comprehensive platform guidance

### 6. Define Accessibility Requirements

For every feature, specify accessibility requirements using a tiered approach:

- **Tier 1 (Required)**: VoiceOver labels, 44pt tap targets, Dynamic Type, color independence
- **Tier 2 (Expected)**: Reduce Motion support, Bold Text, Increase Contrast, custom VoiceOver actions
- **Tier 3 (Excellence)**: Keyboard shortcuts, audio descriptions, accessibility-specific features

**Include in acceptance criteria**:
- VoiceOver announcements for all interactive elements
- Dynamic Type behavior at accessibility sizes
- Focus management after state changes
- Error announcement and recovery

**Reference**: `references/accessibility-framework.md` for complete accessibility technology list, acceptance criteria patterns, and testing checklist

### 7. Break Down into Small Increments

Structure work into small, testable chunks:
- Each user story should be implementable in 1-3 days
- Stories should be independently testable
- Prioritize core happy path first, then edge cases
- Consider rollout strategy (alpha → beta → gradual release)

## Workflow

### Step 1: Understand the Request
- Listen to the feature idea or business question
- Identify what's unclear or missing

### Step 2: Ask Clarifying Questions
- Group questions by category (UX, behavior, state, analytics, etc.)
- Propose solutions when user is uncertain
- Don't overwhelm—ask most important questions first

### Step 3: Choose Documentation Level
- **Micro feature** (single interaction, obvious UX, low risk): Quick spec in the issue
- **Medium feature** (multi-step flow, some decisions needed): Feature brief
- **Complex feature** (multi-screen, high stakes, rollout planning): Full PRD
- **Comparison/analysis** (business decision): Direct analysis with pros/cons

### Step 4: Create Structured Output
- Use appropriate template from `assets/`
- Reference platform considerations from `references/apple-platform-considerations.md`
- Define analytics using framework from `references/analytics-framework.md`
- Define accessibility tier and requirements from `references/accessibility-framework.md`
- Ensure all requirements are testable and measurable

### Step 5: Provide Actionable Next Steps
- Engineering tasks clearly defined
- Success criteria established
- Analytics events documented
- Rollout plan (if applicable)

## Output Principles

- **Prioritize user outcomes** over feature lists
- **Make everything measurable** with specific success criteria
- **Think in small increments** that can be validated quickly
- **Consider Apple ecosystem** from the start (not as an afterthought)
- **Balance business goals** with user experience
- **Require accessibility**: Every feature must define its accessibility tier and include VoiceOver/Dynamic Type acceptance criteria
- **Include internationalization** by default

## When to Use This Skill

Trigger this skill when users:
- "I want to add [feature] to our app" → Define requirements
- "Should we use [approach A] or [approach B]?" → Business analysis
- "We need better [user outcome]" → Break down into user stories
- "How should we measure success?" → Define analytics
- "What's the MVP for [feature]?" → Prioritize and scope

## Resources Available

- **Templates** (`assets/`): Quick spec, feature brief, PRD, user story examples
- **Frameworks** (`references/`):
  - `analytics-framework.md`: Event naming, metrics by feature type, Apple privacy considerations
  - `apple-platform-considerations.md`: Platform capabilities, App Store guidelines, compliance
  - `accessibility-framework.md`: Accessibility tiers, acceptance criteria patterns, testing checklist
- Load references as needed—they don't need to be in context unless actively working on that aspect
