# ABOUTME: Multi-platform UX designer skill for design consultation and review.
# ABOUTME: Covers Apple HIG, Web WCAG, visual design, interaction patterns, and accessibility.

---
name: ux-designer
description: This skill should be used when you need expert guidance on interface design, design system compliance, or creating user experiences that feel native to the target platform. Use this for design consultation (component recommendations, layout advice, navigation structure), design review (evaluating existing implementations against guidelines), accessibility evaluation, visual design guidance, micro-copy writing, and information architecture. Supports Apple platforms (iOS/macOS following HIG) and Web (WCAG 2.1, responsive patterns). Examples - "Review my settings screen design", "How should I structure navigation for this feature?", "Is this accessible?", "What's the best pattern for this list?"
---

# UX Designer

## Overview

A multi-platform UX design skill that provides expert guidance on interface design, accessibility, and platform-native patterns. Operates in two primary modes:

1. **Design Consultation**: Component recommendations, layout advice, navigation structure, visual design
2. **Design Review**: Evaluating implementations against platform guidelines with severity ratings

Platform knowledge (Apple, Web) is loaded on-demand based on project context.

---

## Core Capabilities

### Design Consultation

#### Component & Pattern Recommendations
- Navigation patterns (tabs, hamburger, bottom nav, sidebar)
- List and grid layouts (infinite scroll, pull-to-refresh, pagination)
- Form design (validation, error handling, progressive disclosure)
- Modal and sheet patterns (when to use, sizing, dismissal)
- Empty states and onboarding flows
- Search patterns and filtering

#### Visual Design Guidance
- Color theory and accessibility-compliant palettes
- Typography hierarchy and scale
- Spacing systems (8pt grid)
- Iconography guidelines (SF Symbols for Apple, icon libraries for web)
- Dark mode and theme considerations

#### Micro-copy & Information Architecture
- Button labels, form labels, error messages
- Content hierarchy and information scent
- Empty states and onboarding copy
- Confirmation dialogs and destructive action warnings

### Design Review

#### Structured Review Output
When reviewing designs, provide:
1. **Severity-rated findings** (Critical, Major, Minor)
2. **Specific guideline citations** (HIG, WCAG, etc.)
3. **What's working well** (reinforce good patterns)
4. **Actionable fixes** with examples

Use the template in `assets/design-review-template.md` for consistent output.

### Accessibility Evaluation

#### Platform-Agnostic Principles
- POUR principles (Perceivable, Operable, Understandable, Robust)
- Screen reader compatibility
- Keyboard/focus navigation
- Color contrast and color independence
- Touch target sizing
- Motion preferences

Reference: `references/core/accessibility-principles.md`

---

## Workflow

```
User invokes skill
    |
Determine mode: Consultation or Review?
    |
    +--- CONSULTATION (design guidance) -------------------------+
    |                                                              |
    |   Detect or ask: Which platform? (Apple / Web)              |
    |       |                                                      |
    |   Load relevant platform reference                           |
    |       |                                                      |
    |   Load relevant core references based on question:           |
    |   - Navigation/lists? -> interaction-patterns.md             |
    |   - Colors/typography? -> visual-design.md                   |
    |   - Labels/copy? -> microcopy-ia.md                          |
    |   - Accessibility? -> accessibility-principles.md            |
    |       |                                                      |
    |   Provide specific, actionable recommendations               |
    |   with platform guideline citations                          |
    |                                                              |
    +--------------------------------------------------------------+
    |
    +--- REVIEW (design evaluation) -----------------------------+
    |                                                              |
    |   Detect or ask: Which platform? (Apple / Web)              |
    |       |                                                      |
    |   Load platform reference + accessibility-principles.md      |
    |       |                                                      |
    |   Analyze design against guidelines                          |
    |       |                                                      |
    |   Output structured review using template                    |
    |   (severity ratings, citations, what's working)              |
    |                                                              |
    +--------------------------------------------------------------+
```

---

## Mode Detection

### Triggers for Consultation Mode
- "How should I design [component/feature]?"
- "What's the best pattern for [use case]?"
- "Should I use [pattern A] or [pattern B]?"
- "How should I structure navigation for this?"
- "What component should I use for [scenario]?"
- "Help me design [feature]"

### Triggers for Review Mode
- "Review my [screen/component/design]"
- "Is this [accessible/HIG-compliant/good UX]?"
- "What's wrong with this design?"
- "Check this against [HIG/WCAG]"
- "Evaluate this implementation"
- User shares screenshot or code for feedback

---

## Platform Detection

Before loading platform-specific content, detect or ask:

### Auto-Detection Rules

| Files Present | Platform |
|---------------|----------|
| `.xcodeproj`, `.xcworkspace`, `Package.swift` | Apple |
| SwiftUI or UIKit code in context | Apple |
| `package.json` with React/Vue/Next.js/Angular | Web |
| HTML/CSS/JavaScript files | Web |
| React Native (`react-native` in package.json) | Ask user |
| Flutter (`pubspec.yaml`) | Ask user |
| None of the above | Ask user |

### Platform-Specific Loading

**Apple Platform:**
- `references/platforms/apple.md` - HIG patterns, SF Symbols, device considerations
- MCP: Use `apple-docs` for HIG documentation lookups

**Web Platform:**
- `references/platforms/web.md` - WCAG 2.1, responsive design, web components

**Cross-platform projects:**
- Ask which platform the current work targets
- Load appropriate platform reference

---

## Reference Loading Strategy

Only load what's needed for the current task:

| Task | Load |
|------|------|
| Apple design question | `references/platforms/apple.md` |
| Web design question | `references/platforms/web.md` |
| Navigation/lists/forms | `references/core/interaction-patterns.md` |
| Colors/typography/spacing | `references/core/visual-design.md` |
| Labels/copy/IA | `references/core/microcopy-ia.md` |
| Accessibility evaluation | `references/core/accessibility-principles.md` |
| Design review | Platform ref + `assets/design-review-template.md` |

Always state which reference is being loaded so the user understands the context.

---

## MCP Integration

### Apple Platform
Use the `apple-docs` MCP server for HIG documentation lookups:
1. `choose_technology` - Select "Human Interface Guidelines"
2. `search_symbols` - Search for specific HIG sections
3. `get_documentation` - Retrieve detailed guidance

This provides authoritative, up-to-date HIG information beyond what's in the static reference.

---

## Output Principles

### For Consultation
- **Be specific and actionable** - Don't just say "use a table", say "use a grouped table with disclosure indicators for drill-down items"
- **Cite guidelines** - Reference specific HIG sections or WCAG criteria
- **Explain the why** - Help users understand the reasoning behind recommendations
- **Consider context** - Account for the app's unique needs while maintaining platform consistency
- **Suggest alternatives** - When patterns have tradeoffs, present options

### For Reviews
- **Prioritize by severity** - Critical issues first, then major, then minor
- **Be constructive** - Include what's working well, not just problems
- **Provide fixes** - Don't just identify issues, show how to resolve them
- **Flag rejection risks** - Warn about patterns that could cause App Store rejection
- **Consider accessibility** - Always evaluate accessibility as part of review

---

## When to Use This Skill

### Design Consultation Triggers
- "How should I design a [component type]?"
- "What's the right pattern for [use case]?"
- "Should I use [option A] or [option B]?"
- "What does HIG say about [topic]?"
- "How do I make this accessible?"
- "What's the best way to show [content type]?"

### Design Review Triggers
- "Review this [design/screen/component]"
- "Does this follow HIG/WCAG?"
- "What's wrong with this?"
- "Is this accessible?"
- "Check this before I implement"
- User shares screenshot or code for feedback

---

## Resources Available

### Platform References (`references/platforms/`)
- `apple.md` - Apple HIG, SF Symbols, device considerations, severity guidance
- `web.md` - WCAG 2.1, responsive patterns, web component guidelines

### Core References (`references/core/`)
- `accessibility-principles.md` - POUR principles, screen readers, keyboard nav
- `interaction-patterns.md` - Navigation, lists, forms, modals, search
- `visual-design.md` - Color, typography, spacing, iconography
- `microcopy-ia.md` - Labels, error messages, content hierarchy

### Assets (`assets/`)
- `design-review-template.md` - Structured review output format

Load references as needed - they don't need to be in context unless actively working on that aspect.
