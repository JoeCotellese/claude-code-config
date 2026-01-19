# ABOUTME: Generic PRD template for complex features requiring detailed planning.
# ABOUTME: Platform-agnostic structure; load platform-specific templates for examples.

# [Feature Name] - Product Requirements Document

## Executive Summary

**Feature**: [One-sentence description]

**Business Objective**: [Why are we building this?]

**Target Users**: [Who is this for?]

**Success Metrics**: [1-3 key metrics]

---

## Business Justification

### Problem Statement
[What user problem are we solving? What pain point does this address?]

### Expected Outcomes
- **User Outcome**: [How will users benefit?]
- **Business Outcome**: [How will the business benefit?]
- **Competitive Advantage**: [How does this differentiate us?]

### ROI Estimation
- **Development Effort**: [Small/Medium/Large or estimated weeks]
- **Expected Impact**: [User metric improvements, revenue projections]
- **Priority**: [P0-Critical / P1-High / P2-Medium / P3-Low]

---

## User Stories

### Epic: [High-level feature category]

#### Story 1: [Core functionality]
**As a** [user type]
**I want** [goal/desire]
**So that** [benefit/value]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]

**Analytics Events:**
- `event_name_1` - [When this fires]
- `event_name_2` - [When this fires]

**Edge Cases:**
- [Error scenario 1]: [Expected behavior]
- [Error scenario 2]: [Expected behavior]

**Technical Dependencies:**
- [Required APIs, frameworks, services]

---

#### Story 2: [Supporting functionality]
[Repeat structure above]

---

## Platform Considerations

### Platform-Specific Features
- [Feature 1]: [Yes/No - details if applicable]
- [Feature 2]: [Yes/No - details if applicable]
- [Feature 3]: [Yes/No - details if applicable]

### Cross-Platform
- [Data sync strategy]
- [Device/browser support matrix]

### Accessibility
- **Screen Reader**: [Specific labels and announcements needed]
- **Text Scaling**: [Support for larger text sizes]
- **Motion Preferences**: [Animation alternatives]
- **Keyboard/Switch**: [Full keyboard navigation support]

---

## Analytics Implementation Plan

### Key Events to Track

| Event Name | Trigger | Properties | Purpose |
|------------|---------|------------|---------|
| `viewed_feature_screen` | User enters feature | screen_name, user_id | Track engagement |
| `tapped_primary_action` | User completes action | action_type, success | Track conversions |
| `completed_feature_flow` | User finishes flow | duration, steps_completed | Track success rate |

### Success Metrics

**Primary Metric**: [The one metric that determines success]
- **Target**: [Specific goal, e.g., "20% increase in DAU"]
- **Measurement**: [How we track this]

**Secondary Metrics**:
- [Metric 2]: [Target and measurement]
- [Metric 3]: [Target and measurement]

### Dashboard Requirements
- **Real-time**: [Events that need immediate monitoring]
- **Daily**: [Aggregate metrics reviewed daily]
- **Alerts**: [Thresholds that trigger notifications]

---

## Rollout Strategy

### Phase 1: Internal Testing
- **Audience**: Internal team
- **Success Criteria**: [No critical bugs, core flow works]

### Phase 2: Beta Testing
- **Audience**: [Power users / early adopters]
- **Success Criteria**: [Positive feedback, key metrics trending up]

### Phase 3: Gradual Rollout
- **10%**: Monitor key metrics, catch edge cases
- **50%**: Validate scalability, observe longer-term trends
- **100%**: Full release after confirming stability

### Rollback Plan
- **Trigger Conditions**: [What would cause us to roll back]
- **Rollback Method**: [Feature flag / app update / deployment revert]
- **Communication**: [How to notify affected users]

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Technical risk] | Low/Med/High | Low/Med/High | [How to prevent/address] |
| [User adoption risk] | Low/Med/High | Low/Med/High | [How to prevent/address] |
| [Business risk] | Low/Med/High | Low/Med/High | [How to prevent/address] |

---

## Open Questions

- [ ] [Question requiring clarification]
- [ ] [Question requiring clarification]
- [ ] [Question requiring clarification]

---

## Appendix

### Design Mockups
[Link to design files]

### Technical Specifications
[Link to technical design doc]

### Research & Data
[Links to user research, competitive analysis, usage data]
