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
- **Edge Cases**: What could go wrong? Error states? Permission denials? Network failures?
- **Platform Capabilities**: Should this use widgets? Shortcuts? Live Activities? iCloud sync?

**Do not proceed with full documentation until requirements are clear and complete.**

### 2. Structure Requirements Documents

Once requirements are clear, create structured documentation:

#### For Complex Features: Use PRD Template
- Executive summary with business justification
- Detailed user stories with acceptance criteria
- Analytics implementation plan
- Rollout strategy and risk assessment
- **Location**: `assets/prd-template.md`

#### For Simple Features: Use Feature Brief
- Quick one-page summary format
- Core user flow and success metric
- Technical notes and analytics events
- **Location**: `assets/feature-brief-template.md`

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

### 6. Break Down into Small Increments

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
- **Complex feature** (multi-screen, multiple user flows, high impact): Full PRD
- **Simple feature** (single-screen, straightforward flow): Feature brief
- **Comparison/analysis** (business decision): Direct analysis with pros/cons

### Step 4: Create Structured Output
- Use appropriate template from `assets/`
- Reference platform considerations from `references/apple-platform-considerations.md`
- Define analytics using framework from `references/analytics-framework.md`
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
- **Include accessibility** and internationalization by default

## When to Use This Skill

Trigger this skill when users:
- "I want to add [feature] to our app" → Define requirements
- "Should we use [approach A] or [approach B]?" → Business analysis
- "We need better [user outcome]" → Break down into user stories
- "How should we measure success?" → Define analytics
- "What's the MVP for [feature]?" → Prioritize and scope

## Resources Available

- **Templates** (`assets/`): PRD, feature brief, user story examples
- **Frameworks** (`references/`): Analytics approach, platform considerations
- Load references as needed—they don't need to be in context unless actively working on that aspect
