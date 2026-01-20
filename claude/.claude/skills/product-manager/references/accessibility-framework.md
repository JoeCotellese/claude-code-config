# ABOUTME: Platform-agnostic accessibility framework for product managers.
# ABOUTME: Covers accessibility tiers, acceptance criteria patterns, and testing.

# Accessibility Framework

This reference provides a platform-agnostic approach to accessibility requirements for product features.

For platform-specific implementation details:
- Apple platforms: See `platforms/apple.md`
- Web platforms: See `platforms/web.md`

---

## Why Accessibility Matters

### Business Case
- **Market size**: 15-20% of population has some disability
- **Legal risk**: Accessibility lawsuits increasing (ADA, European Accessibility Act)
- **SEO benefits**: Accessible sites often rank better
- **Universal benefit**: Accessibility features help everyone (captions in noisy environments, large text in bright sunlight)

### User Impact
- Vision: Blindness, low vision, color blindness
- Hearing: Deafness, hard of hearing
- Motor: Limited dexterity, tremors, paralysis
- Cognitive: Learning disabilities, attention disorders, memory issues

---

## Accessibility Tiers

Use this tiered approach to define requirements per feature:

### Tier 1: Required (Must Have)
**Non-negotiable for any feature. Without these, users are blocked.**

| Requirement | Why It Matters |
|-------------|----------------|
| Screen reader labels | Blind users can't interact without them |
| Keyboard access | Motor-impaired users can't use mouse |
| Minimum touch/click targets | Users with tremors miss small targets |
| Text scaling | Low-vision users can't read small text |
| Color independence | Color-blind users miss color-only info |
| Logical reading order | Screen readers read in wrong sequence |
| Focus management | Users lose their place after actions |
| Error identification | Users can't fix problems they can't find |

### Tier 2: Expected (Should Have)
**Standard for quality products. Missing these frustrates users.**

| Requirement | Why It Matters |
|-------------|----------------|
| Motion reduction | Vestibular disorders triggered by animation |
| High contrast support | Low-vision users need stronger contrast |
| Bold text support | Some users need heavier font weights |
| Grouped actions | Reduces interaction steps for assistive tech |
| State announcements | Dynamic content changes need to be announced |

### Tier 3: Excellence (Nice to Have)
**Differentiators for accessibility-focused products.**

| Requirement | Why It Matters |
|-------------|----------------|
| Full keyboard shortcuts | Power users and motor-impaired efficiency |
| Audio descriptions | Blind users understand video content |
| Haptic feedback | Deaf users get tactile confirmation |
| Per-user customization | Users can tune to their specific needs |

---

## Acceptance Criteria Patterns

Use these patterns in user stories:

### For Interactive Elements (Buttons, Links, Controls)

```
Given screen reader is enabled
When user focuses on [element]
Then screen reader announces "[label]" as a [role]
And hint "[usage description]" is announced (if applicable)
```

Example:
```
Given screen reader is enabled
When user focuses on the share button
Then screen reader announces "Share recipe" as a button
And hint "Opens share menu" is announced
```

### For Images and Media

```
Given screen reader is enabled
When user focuses on [image/media]
Then screen reader announces "[meaningful description]"
OR the element is hidden from screen reader (if decorative)
```

### For Dynamic Content

```
Given screen reader is enabled
When [content changes/loads/updates]
Then screen reader announces the change appropriately
And focus moves to [logical location] (if applicable)
```

### For Forms

```
Given screen reader is enabled
When user submits form with invalid data
Then the error is announced immediately
And focus moves to the first invalid field
And the field's error message is part of its accessible description
```

### For Text Scaling

```
Given user has set text size to [largest accessibility size]
When viewing [screen/component]
Then all text is legible and not truncated
And layout adapts without horizontal scrolling
And no content is clipped or hidden
```

### For Keyboard Navigation

```
Given user is navigating with keyboard only
When user presses Tab through [component]
Then focus moves in logical order
And all interactive elements are reachable
And focus indicator is clearly visible
```

### For Motion Preferences

```
Given user has enabled reduced motion preference
When viewing [animation/transition]
Then animation is replaced with instant state change
OR animation duration is significantly reduced
```

---

## Common Patterns by Feature Type

### Lists and Tables

- [ ] Announce item count when entering list
- [ ] Each row fully describes its content
- [ ] Actions (swipe, context menu) available via accessible alternatives
- [ ] Loading states announced
- [ ] Empty states announced

### Forms

- [ ] Labels associated with inputs
- [ ] Required fields indicated in label
- [ ] Errors announced and associated with fields
- [ ] Clear/reset buttons labeled descriptively
- [ ] Autocomplete suggestions announced

### Navigation

- [ ] Current location announced on screen/page change
- [ ] Back button has destination label (not just "Back")
- [ ] Tab/nav bar announces selection state
- [ ] Skip links for repeated content (web)

### Media Players

- [ ] All controls labeled
- [ ] Current time/duration accessible
- [ ] Captions available for video
- [ ] Transcript available for audio
- [ ] Keyboard controls work

### Dialogs and Modals

- [ ] Focus moves to dialog when opened
- [ ] Dialog content announced automatically
- [ ] Buttons labeled with their action
- [ ] Focus returns to trigger when closed
- [ ] Escape key closes dialog

### Notifications and Alerts

- [ ] Important alerts announced automatically
- [ ] Dismiss action accessible
- [ ] Don't disappear too quickly (5+ seconds)
- [ ] Don't block interaction with rest of app

---

## Testing Checklist

### Manual Testing (Required)

| Test | Method |
|------|--------|
| Screen reader walkthrough | Navigate entire feature with screen reader, eyes closed |
| Keyboard-only navigation | Unplug mouse, complete all tasks with keyboard |
| Text scaling extremes | Test at smallest and largest text sizes |
| Color blindness | Use simulator or grayscale mode |
| Motion reduction | Enable reduced motion, verify alternatives |
| High contrast | Enable high contrast mode |

### Automated Testing

- Run accessibility audit tools (axe, Lighthouse, Xcode Inspector)
- Include accessibility checks in CI/CD
- Validate HTML/ARIA patterns

### User Testing

For major features, include users who rely on assistive technology:
- Screen reader users (blind/low vision)
- Keyboard-only users (motor impairments)
- Users with cognitive disabilities
- Users with hearing impairments

---

## Analytics for Accessibility

Track accessibility technology usage (while respecting privacy):

### Useful Signals
- % of sessions with screen reader active
- % of sessions with larger text sizes
- % of sessions with reduced motion enabled
- % of sessions with high contrast enabled

### Analyze
- **Task completion rates** by accessibility state
- **Error rates** by accessibility state
- **Time on task** by accessibility state
- **Drop-off points** for assistive tech users

### Privacy Note
- Only collect aggregate data
- Don't identify individual users by accessibility settings
- Use to improve product, not to profile users

---

## Common Mistakes

### 1. Accessibility as Afterthought
Adding accessibility after development is expensive. Design for accessibility from the start.

### 2. Screen Reader = All Accessibility
Screen readers serve blind users. Don't forget motor, cognitive, hearing, and low-vision needs.

### 3. Automated Testing Only
Automated tools catch ~30% of issues. Manual testing with real assistive technology is essential.

### 4. "Users Can Work Around It"
Workarounds are exhausting. Small friction multiplied by every interaction = abandonment.

### 5. Assuming One Size Fits All
Different disabilities have different (sometimes conflicting) needs. Offer customization where possible.

---

## Resources

### Guidelines
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - Web Content Accessibility Guidelines
- [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Material Design: Accessibility](https://material.io/design/usability/accessibility.html)

### Testing Tools
- [axe DevTools](https://www.deque.com/axe/) - Browser extension
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Chrome DevTools
- [Accessibility Inspector](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/OSXAXTestingApps.html) - Xcode

### Screen Readers
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (Apple, built-in)
- TalkBack (Android, built-in)

### Learning
- [WebAIM](https://webaim.org/) - Web accessibility resources
- [A11y Project](https://www.a11yproject.com/) - Community resources
- [Deque University](https://dequeuniversity.com/) - Training
