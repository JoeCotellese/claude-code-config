# ABOUTME: Structured template for design review output.
# ABOUTME: Provides consistent format with severity ratings, guideline citations, and actionable fixes.

# Design Review Template

Use this template for structured design review output. Adapt sections as needed based on review scope.

---

## Review Output Format

```markdown
# Design Review: [Screen/Component Name]

**Platform:** [Apple iOS / Apple macOS / Web / Cross-platform]
**Review Date:** [Date]
**Reviewer:** Claude (UX Designer Skill)

---

## Summary

[2-3 sentence overview of the design being reviewed and high-level assessment]

---

## What's Working Well

- [Positive observation with specific reference]
- [Positive observation with specific reference]
- [Positive observation with specific reference]

---

## Findings

### Critical Issues

Issues that will likely cause App Store rejection, significant accessibility barriers, or make features unusable.

#### [Issue Title]
**Severity:** Critical
**Guideline:** [HIG section / WCAG criterion]
**Location:** [Where in the design]

**Problem:**
[Clear description of what's wrong]

**Impact:**
[Who is affected and how]

**Recommended Fix:**
[Specific, actionable solution]

---

### Major Issues

Issues that significantly degrade user experience or violate platform conventions.

#### [Issue Title]
**Severity:** Major
**Guideline:** [HIG section / WCAG criterion]
**Location:** [Where in the design]

**Problem:**
[Clear description of what's wrong]

**Recommended Fix:**
[Specific, actionable solution]

---

### Minor Issues

Polish improvements and missed opportunities.

#### [Issue Title]
**Severity:** Minor
**Guideline:** [HIG section / WCAG criterion if applicable]
**Location:** [Where in the design]

**Observation:**
[Description]

**Suggestion:**
[Optional improvement]

---

## Accessibility Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| Color contrast | Pass/Fail/Check | |
| Touch targets (44pt min) | Pass/Fail/Check | |
| VoiceOver labels | Pass/Fail/Check | |
| Dynamic Type support | Pass/Fail/Check | |
| Color independence | Pass/Fail/Check | |
| Focus management | Pass/Fail/Check | |
| Reduce Motion support | Pass/Fail/Check | |

---

## Recommendations Summary

### Must Fix (Before Release)
1. [Critical issue 1]
2. [Critical issue 2]

### Should Fix (High Priority)
1. [Major issue 1]
2. [Major issue 2]

### Consider (When Time Permits)
1. [Minor issue 1]
2. [Minor issue 2]

---

## References Consulted

- [List of HIG sections, WCAG criteria, or other guidelines referenced]
```

---

## Severity Definitions

### Critical
- **App Store impact:** Likely rejection
- **User impact:** Feature unusable for some users
- **Accessibility:** Fails WCAG A or major Apple accessibility requirement
- **Action:** Must fix before release

**Examples:**
- Missing VoiceOver labels on interactive elements
- Touch targets below 44×44 points
- Color-only information conveyance
- Text that doesn't support Dynamic Type
- Keyboard traps

### Major
- **User impact:** Significant friction or confusion
- **Platform:** Clear HIG/WCAG violation
- **Accessibility:** Fails WCAG AA
- **Action:** Should fix before release

**Examples:**
- Non-standard navigation patterns
- Missing haptic feedback on expected actions
- Inconsistent use of SF Symbols
- Poor contrast ratios (below 4.5:1)
- Missing empty states
- Confusing button labels

### Minor
- **User impact:** Small polish issue
- **Platform:** Suboptimal but acceptable
- **Accessibility:** Enhancement opportunity
- **Action:** Fix when time permits

**Examples:**
- Could use more appropriate SF Symbol
- Spacing slightly off from 8pt grid
- Animation timing could be refined
- Could add VoiceOver hints
- Minor copy improvements

---

## Platform-Specific Sections

### Apple Platform Addition

```markdown
## Apple-Specific Considerations

### SF Symbols
- [ ] Using appropriate SF Symbols for system actions
- [ ] Symbol weight matches text weight
- [ ] Rendering mode appropriate for context

### Dark Mode
- [ ] Tested in both light and dark mode
- [ ] Using semantic colors (not hardcoded)
- [ ] Sufficient contrast in both modes

### Device Adaptation
- [ ] Safe areas respected
- [ ] Dynamic Island/notch handled appropriately
- [ ] iPad layout considered (if universal app)

### Native Feel
- [ ] Standard iOS/macOS patterns used where appropriate
- [ ] System controls preferred over custom
- [ ] Animations match platform conventions
```

### Web Platform Addition

```markdown
## Web-Specific Considerations

### Responsive Design
- [ ] Mobile breakpoint tested
- [ ] Tablet breakpoint tested
- [ ] Desktop breakpoint tested
- [ ] Content reflows appropriately

### Keyboard Navigation
- [ ] All interactive elements focusable
- [ ] Focus indicator visible
- [ ] Tab order logical
- [ ] Skip link present

### Screen Reader
- [ ] ARIA landmarks present
- [ ] Headings hierarchy logical
- [ ] Form labels associated
- [ ] Live regions for dynamic content

### Browser Support
- [ ] Tested in Chrome
- [ ] Tested in Firefox
- [ ] Tested in Safari
- [ ] Graceful degradation for older browsers
```

---

## Quick Checklist Format

For faster reviews, use this condensed format:

```markdown
# Quick Review: [Component]

## Pass
- [x] Touch targets ≥ 44pt
- [x] Color contrast ≥ 4.5:1
- [x] VoiceOver labels present

## Needs Attention
- [ ] **Critical:** [Issue] → [Fix]
- [ ] **Major:** [Issue] → [Fix]
- [ ] **Minor:** [Issue] → [Fix]

## Notes
[Any additional observations]
```
