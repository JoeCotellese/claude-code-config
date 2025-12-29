# Accessibility Framework for Apple Platforms

## Overview

Apple considers accessibility a core value, not an afterthought. Apps that fail basic accessibility requirements risk App Store rejection and exclude ~15-20% of users who rely on assistive technologies. This framework defines accessibility requirements from a product perspective.

## Apple's Accessibility Technologies

### Vision

| Technology | What It Does | Product Requirement |
|------------|--------------|---------------------|
| **VoiceOver** | Screen reader for blind/low-vision users | All interactive elements must have labels |
| **Dynamic Type** | System-wide text size adjustment | Text must scale from 50% to 310% of default |
| **Bold Text** | Increases font weight system-wide | Respect `legibilityWeight` trait |
| **Increase Contrast** | Enhances visual distinction | Support high-contrast color variants |
| **Reduce Transparency** | Removes blur/transparency effects | Provide solid background alternatives |
| **Reduce Motion** | Minimizes animations | Provide static alternatives to animations |
| **Differentiate Without Color** | Adds shapes/labels to color-coded info | Never rely on color alone |

### Motor

| Technology | What It Does | Product Requirement |
|------------|--------------|---------------------|
| **Switch Control** | Navigate via external switches | All functions reachable without gestures |
| **Voice Control** | Control device by voice | Elements must have accessible names |
| **AssistiveTouch** | Custom gestures and buttons | Support standard tap targets (44x44pt minimum) |
| **Dwell Control** | Activate by hovering/dwelling | Interactive elements clearly defined |
| **Full Keyboard Access** | Navigate via keyboard (iPadOS/macOS) | Logical focus order, visible focus indicators |

### Hearing

| Technology | What It Does | Product Requirement |
|------------|--------------|---------------------|
| **Closed Captions** | Text for audio content | Provide captions for all video/audio |
| **Mono Audio** | Combines stereo channels | Audio must be understandable in mono |
| **Visual Alerts** | Flash screen for notifications | Don't rely solely on audio cues |

### Cognitive

| Technology | What It Does | Product Requirement |
|------------|--------------|---------------------|
| **Guided Access** | Locks device to single app | App must function in restricted mode |
| **Speak Screen** | Reads entire screen aloud | Content must be in logical reading order |
| **Reading Content** | Highlights words as read | Text must be actual text, not images |

## Accessibility Tiers

### Tier 1: Required (Must Have)

These are non-negotiable for any feature:

- [ ] **VoiceOver labels**: All buttons, images, and controls have descriptive labels
- [ ] **VoiceOver hints**: Complex controls have usage hints
- [ ] **Tap targets**: Minimum 44x44 points for all interactive elements
- [ ] **Dynamic Type**: Text scales with system settings (use system fonts or scaled custom fonts)
- [ ] **Color independence**: Information never conveyed by color alone
- [ ] **Logical reading order**: VoiceOver reads content in sensible sequence
- [ ] **Focus management**: Focus moves logically after state changes/navigation
- [ ] **Error identification**: Errors clearly announced and actionable

### Tier 2: Expected (Should Have)

Standard for quality apps:

- [ ] **Reduce Motion**: Provide alternatives to complex animations
- [ ] **Bold Text**: Respect system bold text preference
- [ ] **Increase Contrast**: Support higher contrast when enabled
- [ ] **Custom actions**: Group related actions for VoiceOver efficiency
- [ ] **Accessibility value**: Dynamic content (sliders, progress) announces current value
- [ ] **Semantic containers**: Use `accessibilityElement(children:)` to group related content
- [ ] **Rotor support**: Custom rotors for efficient navigation in content-heavy screens

### Tier 3: Excellence (Nice to Have)

Differentiators for accessibility-focused apps:

- [ ] **Per-app text size**: App-specific Dynamic Type override in Settings
- [ ] **Audio descriptions**: Narration of visual content in videos
- [ ] **Haptic feedback**: Tactile confirmation for actions
- [ ] **Keyboard shortcuts**: Full keyboard navigation (iPadOS/macOS)
- [ ] **Accessibility-specific features**: Dedicated accessibility settings within app

## Acceptance Criteria Patterns

### For Buttons/Controls

```
Given VoiceOver is enabled
When the user focuses on [button/control]
Then VoiceOver announces "[descriptive label]" as a [button/link/etc.]
And the hint "[how to use]" is announced (if applicable)
```

### For Images

```
Given VoiceOver is enabled
When the user focuses on [image]
Then VoiceOver announces "[meaningful description]"
OR the image is hidden from VoiceOver (if decorative)
```

### For Dynamic Content

```
Given VoiceOver is enabled
When [content changes/loads/updates]
Then VoiceOver announces the change appropriately
And focus moves to logical location (if applicable)
```

### For Forms

```
Given VoiceOver is enabled
When the user submits the form with invalid data
Then the error is announced immediately
And focus moves to the first invalid field
And the field's error message is part of its accessible description
```

### For Dynamic Type

```
Given the user has set text size to [largest accessibility size]
When viewing [screen/component]
Then all text is legible and not truncated
And layout adapts without horizontal scrolling
And no content is clipped or hidden
```

## Testing Checklist

### Manual Testing (Required)

1. **VoiceOver walkthrough**: Navigate entire feature with VoiceOver, eyes closed
2. **Dynamic Type extremes**: Test at smallest and largest accessibility sizes
3. **Bold Text**: Enable and verify text weights increase
4. **Reduce Motion**: Verify animations have static alternatives
5. **Increase Contrast**: Verify UI remains visible and distinct
6. **Invert Colors**: Verify images and UI are still usable (Smart Invert)
7. **Keyboard navigation**: Test full feature with external keyboard (iPadOS)

### Automated Testing

- Use Xcode Accessibility Inspector during development
- Run `accessibilityAudit()` in XCTest UI tests
- Check for missing labels in SwiftUI previews

### User Testing

For major features, include users who rely on assistive technology in beta testing.

## Common Patterns by Feature Type

### Lists/Tables

- Announce item count when entering list
- Each row fully describes its content
- Actions (swipe actions, context menus) available via VoiceOver actions
- Loading states announced

### Forms

- Labels associated with inputs
- Required fields indicated in label
- Errors announced and associated with fields
- Clear button labeled (not just "X")

### Media Players

- All controls labeled
- Current time/duration accessible
- Captions available for video
- Transcript available for audio-only

### Navigation

- Current location announced on screen change
- Back button has destination label ("Back to Recipes" not just "Back")
- Tab bar announces selection state
- Modal presentation announced

### Alerts/Dialogs

- Focus moves to alert when presented
- Alert content announced automatically
- Buttons clearly labeled with their action

## App Store Considerations

Apple may reject apps for:

- Missing VoiceOver labels on critical UI
- Tap targets below 44x44 points
- Text that doesn't scale with Dynamic Type
- Color-only information with no alternative
- Inaccessible onboarding blocking app usage

## Analytics for Accessibility

Track accessibility technology usage (respecting privacy):

```swift
// Check if VoiceOver is active
UIAccessibility.isVoiceOverRunning

// Check if larger text sizes enabled
UIApplication.shared.preferredContentSizeCategory.isAccessibilityCategory

// Check if reduce motion enabled
UIAccessibility.isReduceMotionEnabled
```

Consider tracking:

- **Accessibility tech active**: What percentage of sessions use VoiceOver, larger text, etc.
- **Task completion by accessibility state**: Do users with assistive tech complete key flows?
- **Accessibility-specific errors**: Are there flows that fail more often with accessibility enabled?

## Resources

- [Apple Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Apple Accessibility Programming Guide](https://developer.apple.com/accessibility/)
- [WWDC Accessibility Sessions](https://developer.apple.com/videos/accessibility)
