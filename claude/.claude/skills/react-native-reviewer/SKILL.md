---
name: react-native-reviewer
description: This skill should be used to review React Native and TypeScript code for quality, best practices, and idiomatic patterns. Use this skill on-demand when the user requests a code review, or proactively before commits when React Native code has been written or modified. The skill provides educational feedback explaining WHY patterns are recommended and suggests alternatives.
---

# React Native Code Reviewer

## Overview

Perform comprehensive React Native and TypeScript code reviews with educational explanations. This skill reviews code quality, React patterns, performance, accessibility, and testing practices. Designed for developers learning React, it explains the reasoning behind recommendations and suggests idiomatic alternatives.

## When to Use

- **On-demand**: When the user explicitly requests a code review of React Native code
- **Before commits**: Proactively after writing or modifying React Native/TypeScript code, before committing
- **After implementing features**: To catch anti-patterns before they become entrenched

## Review Process

### Step 1: Identify Files to Review

Determine which files need review:
- For on-demand reviews: Review files specified by user or recently modified `.tsx`/`.ts` files in `src/`
- For pre-commit reviews: Check `git diff --staged --name-only` for React Native files

### Step 2: Load Relevant References

Based on the code being reviewed, load appropriate reference files from `references/`:

| Code Pattern | Reference to Load |
|--------------|-------------------|
| Hooks (useState, useEffect, etc.) | `references/hooks-patterns.md` |
| Recoil atoms/selectors | `references/recoil-patterns.md` |
| Component structure, props | `references/component-patterns.md` |
| FlatList, images, animations | `references/performance-checklist.md` |
| accessibilityLabel, roles | `references/accessibility.md` |
| Test files (*.test.tsx) | `references/testing-patterns.md` |

### Step 3: Review Categories

Review each file against these categories, loading the relevant reference as needed:

#### 3.1 Hooks Usage
- Rules of hooks compliance
- Dependency array correctness
- Stale closure prevention
- Appropriate use of useMemo/useCallback
- Custom hook design

#### 3.2 Component Design
- Props interface clarity and typing
- Component composition patterns
- Conditional rendering correctness
- Render optimization (memo usage)
- Platform-specific handling

#### 3.3 State Management (Recoil)
- Atom granularity (not too large)
- Selector usage for derived state
- Key uniqueness and naming
- Appropriate hook selection (useRecoilValue vs useSetRecoilState)

#### 3.4 Performance
- Unnecessary re-renders
- FlatList optimization props
- Image handling
- Animation patterns

#### 3.5 Accessibility
- accessibilityLabel on interactive elements
- accessibilityRole usage
- Touch target sizes
- Color contrast considerations

#### 3.6 TypeScript
- Proper typing (avoid `any`)
- Interface vs type usage
- Generic patterns
- Null handling

#### 3.7 Testing (if test files present)
- Testing Library query priority
- Behavior vs implementation testing
- Async testing patterns
- Mock appropriateness

### Step 4: Report Format

Structure the review report as follows:

```markdown
## Code Review: [filename]

### Summary
[1-2 sentence overview of code quality]

### Issues Found

#### 🔴 Critical (Must Fix)
[Issues that will cause bugs or major problems]

#### 🟡 Recommended (Should Fix)
[Non-idiomatic patterns, performance issues, accessibility gaps]

#### 🟢 Suggestions (Nice to Have)
[Minor improvements, style preferences]

### Issue Details

For each issue:

**[Category] Issue title**
- **Location**: `file:line`
- **Current code**:
```tsx
// problematic code
```
- **Why this is problematic**: [Educational explanation]
- **Suggested fix**:
```tsx
// improved code
```
- **Learn more**: See `references/[relevant-file].md`

### What's Good ✓
[Highlight patterns done well - positive reinforcement]
```

## Project-Specific Patterns

This skill is aware of the Wavely project structure:

### Directory Structure
- Components: `src/components/[Name]/index.tsx`
- Hooks: `src/hooks/use[Name].ts`
- State: `src/state/[name]State.ts`
- APIs: `src/apis/[Name]Api.ts`
- Interfaces: `src/interfaces/[Name].ts`

### Existing Patterns to Follow
- Recoil for global state (atoms in `src/state/`)
- Custom hooks encapsulate business logic
- React Navigation with native stack
- BaseApi pattern for API calls
- Jest with react-native-accessibility-engine for testing

## Quick Reference Searches

To find specific patterns in reference files:

```bash
# Hooks patterns
rg "useEffect|useState|useMemo|useCallback" references/hooks-patterns.md

# Performance issues
rg "❌|Anti-Pattern" references/performance-checklist.md

# Accessibility requirements
rg "accessibilityLabel|accessibilityRole" references/accessibility.md

# Testing queries
rg "getBy|queryBy|findBy" references/testing-patterns.md
```

## Educational Mode

Since this skill serves a developer learning React Native:

1. **Always explain WHY** - Don't just say "use useCallback here", explain that it prevents child re-renders by maintaining referential equality
2. **Show the contrast** - Provide before/after code snippets
3. **Reference the docs** - Point to specific sections in reference files for deeper learning
4. **Celebrate wins** - Acknowledge good patterns to reinforce learning
5. **Prioritize clearly** - New developers need to know what's critical vs nice-to-have
