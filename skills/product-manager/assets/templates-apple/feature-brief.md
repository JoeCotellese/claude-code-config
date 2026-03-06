
# [Feature Name] - Feature Brief (Apple)
**Quick reference for lightweight feature planning. Use PRD template for complex features.**

---

## Summary

**What**: [One sentence describing the feature]

**Why**: [Primary business/user value]

**Who**: [Target user segment]

**Priority**: [P0-Critical / P1-High / P2-Medium / P3-Low]

---

## Objectives

### User Objective
[What problem does this solve for users?]

### Business Objective
[What business goal does this achieve?]

### Success Metric
[One key metric that defines success]
- Target: [Specific goal]

---

## User Experience

### Happy Path
1. User [action 1]
2. App [response 1]
3. User [action 2]
4. App [response 2]
5. Result: [outcome]

### Key Interactions
- **Primary Action**: [What the user does]
- **Visual Feedback**: [What the user sees]
- **Confirmation**: [How success is communicated - haptic, sound, visual]

---

## Apple Platform Integration

### iOS/iPadOS Features
- [ ] **Widget**: [Home Screen / Lock Screen / StandBy support?]
- [ ] **Live Activity**: [Real-time updates needed?]
- [ ] **Shortcuts**: [Siri Shortcuts integration?]
- [ ] **Focus Filters**: [App behavior in Focus modes?]

### Apple Ecosystem
- [ ] **iCloud Sync**: [What data syncs?]
- [ ] **Handoff**: [Continuity between devices?]
- [ ] **SharePlay**: [Shared experiences?]

### Device Support
- iPhone: [Required / Optimized / N/A]
- iPad: [Required / Optimized / N/A]
- Mac: [Required / Optimized / N/A]
- Apple Watch: [Required / Optimized / N/A]

---

## Technical Notes

### Requirements
- [API/service needed]
- [Framework needed - SwiftUI, UIKit, etc.]
- [Permissions required - notifications, camera, location, etc.]

### Constraints
- [iOS version minimum]
- [Device limitations]
- [Offline behavior]

---

## Analytics

### Track These Events
- `event_name` - [When it fires]
- `event_name` - [When it fires]

### Monitor This Metric
[Primary success metric and how to measure it]

### Apple Privacy Compliance
- [ ] No cross-app tracking without ATT consent
- [ ] Privacy Nutrition Label updated
- [ ] User can opt-out of analytics

---

## Accessibility (Tier 1 Required)

- [ ] **VoiceOver**: All controls have labels and hints
- [ ] **Dynamic Type**: Text scales from 50% to 310%
- [ ] **Tap Targets**: Minimum 44x44pt
- [ ] **Color Independence**: No color-only information
- [ ] **Reduce Motion**: Static alternatives to animations
- [ ] **Bold Text**: Respects system bold preference

---

## Done When

- [ ] Core functionality works on iPhone
- [ ] iPad layout adapts appropriately
- [ ] Accessibility Tier 1 complete
- [ ] Analytics implemented
- [ ] Tested on TestFlight

---

## Risks

| Risk | Mitigation |
|------|------------|
| App Store rejection | [Review guidelines before submission] |
| [Technical risk] | [How to address] |

---

## Example: Meal Planning Calendar

### Summary

**What**: Visual calendar to plan recipes for the week.

**Why**: Users want to organize cooking around their schedule.

**Who**: Organized home cooks who meal prep.

**Priority**: P1-High

### Objectives

**User Objective**: Reduce decision fatigue about what to cook each day.

**Business Objective**: Increase weekly retention by making app essential to routine.

**Success Metric**: Weekly Active Users (WAU)
- Target: 15% increase in WAU within 8 weeks

### User Experience

**Happy Path**:
1. User taps Calendar tab
2. App shows current week with empty meal slots
3. User taps empty slot → recipe picker appears
4. User selects recipe → slot fills with recipe thumbnail
5. Result: Week's meals planned, shopping list auto-generated

### Apple Platform Integration

- [x] **Widget**: Medium widget shows today's planned meals
- [ ] **Live Activity**: Not applicable
- [x] **Shortcuts**: "Plan this recipe for [day]"
- [x] **iCloud Sync**: Calendar syncs across devices

### Accessibility

- [x] VoiceOver: "Monday dinner, empty. Double tap to add recipe."
- [x] Dynamic Type: Calendar scales, shows abbreviated text at largest sizes
- [x] Reduce Motion: No swipe animations, instant navigation
