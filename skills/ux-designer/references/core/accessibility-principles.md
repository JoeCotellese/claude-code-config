
# Accessibility Principles
This reference covers platform-agnostic accessibility principles that apply to both Apple and Web platforms. For platform-specific implementation details, see the respective platform references.

---

## POUR Principles

The Web Content Accessibility Guidelines (WCAG) are organized around four principles, collectively known as POUR. These principles apply equally to native apps.

### Perceivable

Users must be able to perceive the information being presented. It cannot be invisible to all of their senses.

**Key Requirements:**
- **Text alternatives**: Meaningful images have descriptions
- **Time-based media**: Captions, transcripts, audio descriptions
- **Adaptable content**: Content can be presented in different ways
- **Distinguishable**: Content is easy to see and hear

**Common Failures:**
- Images without alt text
- Videos without captions
- Color as only means of conveying information
- Text too small to read
- Insufficient color contrast

### Operable

Users must be able to operate the interface. The interface cannot require interaction that a user cannot perform.

**Key Requirements:**
- **Keyboard accessible**: All functionality via keyboard
- **Enough time**: Users can complete tasks without time limits
- **No seizure triggers**: No flashing content (3x/second)
- **Navigable**: Clear navigation, focus management
- **Input modalities**: Multiple ways to interact

**Common Failures:**
- Mouse-only interactions
- Keyboard traps
- Time limits without extension options
- Flashing or strobing content
- No skip navigation

### Understandable

Users must be able to understand the information and interface operation.

**Key Requirements:**
- **Readable**: Text is readable and understandable
- **Predictable**: Interface behaves predictably
- **Input assistance**: Help users avoid and correct mistakes

**Common Failures:**
- Jargon without explanation
- Inconsistent navigation
- Form errors without clear guidance
- Unexpected context changes
- No help for complex tasks

### Robust

Content must be robust enough to work with current and future technologies, including assistive technologies.

**Key Requirements:**
- **Compatible**: Works with assistive technologies
- **Valid markup**: Proper HTML/platform semantics
- **Status messages**: Changes announced appropriately

**Common Failures:**
- Invalid HTML structure
- Custom widgets without ARIA/accessibility traits
- Dynamic content not announced
- Incompatibility with screen readers

---

## Screen Reader Basics

### How Screen Readers Work
Screen readers translate visual interfaces into audio (or braille). They:
- Read text content aloud
- Announce element types (button, link, heading)
- Describe relationships (list of 5 items, menu expanded)
- Navigate by landmarks, headings, links, form fields

### What Screen Readers Need

| Information | How to Provide |
|-------------|----------------|
| **Name** | Label, alt text, button text |
| **Role** | Semantic element or ARIA role |
| **State** | selected, expanded, checked, disabled |
| **Value** | Current value of sliders, inputs |
| **Description** | Additional context via hints |

### Common Screen Readers

| Platform | Screen Reader |
|----------|---------------|
| iOS/macOS | VoiceOver (built-in) |
| Windows | NVDA (free), JAWS (paid) |
| Android | TalkBack (built-in) |
| Web | Varies by user's platform |

### Testing with Screen Readers
1. Turn on the screen reader
2. Navigate without looking at the screen
3. Can you complete the task?
4. Is information announced in logical order?
5. Are interactive elements clearly identified?

---

## Color Independence

### The Principle
Never use color as the only means of conveying information.

### Common Violations

| Bad Example | Why It Fails | Good Example |
|-------------|--------------|--------------|
| Red text for errors | Color blind users miss it | Red text + error icon + "Error:" prefix |
| Green/red status dots | Indistinguishable | Dots + labels: "Active", "Inactive" |
| Colored graph lines | Can't differentiate | Different line patterns + legend |
| Link in blue text only | Might miss in grayscale | Underline + color |

### Color Blindness Types

| Type | Prevalence | Confusion |
|------|------------|-----------|
| **Deuteranopia** (red-green) | ~6% of males | Red/green/brown |
| **Protanopia** (red-green) | ~2% of males | Similar to above |
| **Tritanopia** (blue-yellow) | Rare | Blue/yellow |
| **Monochromacy** | Very rare | All colors |

### Best Practices
- Use icons + color + text together
- Test with color blindness simulators
- Ensure sufficient contrast regardless of hue
- Don't rely on red/green distinction

---

## Touch Targets

### Minimum Sizes

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| Apple (iOS) | 44×44 pt | 48×48 pt |
| Web/Android | 44×44 px | 48×48 px |
| Apple Watch | 38×38 pt | - |

### Why This Matters
- Motor impairments make precise tapping difficult
- Finger pads are ~10mm across
- Errors frustrate users and cause mistakes
- Small targets are accessibility barriers

### Implementation Tips
- Visual element can be smaller than touch area
- Use padding to increase hit area
- Ensure spacing between adjacent targets (8px min)
- Test on actual devices with fingers, not mouse

---

## Focus Management

### When Focus Management is Required
- Modal dialogs open (focus into modal)
- Modal dialogs close (focus back to trigger)
- Content dynamically appears
- Navigation within single-page apps
- After form submission with errors
- Accordion/disclosure expands

### Focus Principles
1. **Focus should be visible** - Users must see what's focused
2. **Focus order should be logical** - Usually matches visual order
3. **Focus should not be trapped** - Users can always escape
4. **Focus should follow user intent** - Move focus where attention goes

### Common Focus Issues
- Focus lost after modal closes
- Focus jumps unexpectedly
- Focus indicator removed for aesthetics
- Tab order doesn't match visual order
- Focus trapped in widget

---

## Motion Preferences

### Reduce Motion Setting
Both iOS and Web provide settings for users who are affected by motion:
- Vestibular disorders (dizziness, nausea)
- Motion sensitivity
- Cognitive conditions
- User preference

### Respecting Motion Preferences

**iOS (SwiftUI):**
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? nil : .spring()) {
    // Animation
}
```

**Web (CSS):**
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

### What to Reduce
- Parallax effects
- Zooming/scaling animations
- Sliding page transitions
- Auto-playing videos
- Infinite scrolling animations

### What to Keep
- Opacity fades (generally safe)
- Loading indicators (functional)
- Progress feedback (necessary)
- Focus indicators (accessibility requirement)

---

## Text Scaling

### User Preferences
Users may need larger text due to:
- Vision impairments
- Aging
- Device distance
- Personal preference

### Platform Support

| Platform | Feature | Range |
|----------|---------|-------|
| iOS | Dynamic Type | 50% - 310% |
| Web | Browser zoom | Typically 100% - 500% |
| Web | Text-only zoom | Varies |

### Requirements
- Text must scale without loss of content or functionality
- Layouts should adapt (reflow, not just clip)
- Test at largest accessibility sizes
- Don't use fixed pixel sizes for text

### Common Issues
- Text truncated at larger sizes
- Layouts break at larger sizes
- Fixed-height containers clip text
- Text overlaps other elements

---

## Cognitive Accessibility

### Principles
- **Clear language**: Avoid jargon, use simple words
- **Consistent navigation**: Same location, same behavior
- **Clear errors**: What went wrong, how to fix it
- **Minimize memory load**: Don't require remembering across screens
- **Allow time**: No arbitrary time limits

### Helpful Patterns
- Clear headings that describe content
- Chunked content (not walls of text)
- Visual hierarchy showing importance
- Progress indicators for multi-step tasks
- Confirmation before destructive actions
- Undo capability where possible

---

## Accessibility Testing Approach

### Automated Testing
Catches ~30% of issues:
- Color contrast
- Missing alt text
- Missing form labels
- Heading structure
- ARIA attribute validity

### Manual Testing
Required for the remaining ~70%:
- Screen reader usability
- Keyboard navigation flow
- Focus management
- Content understanding
- Task completion

### Testing Checklist

| Category | Test |
|----------|------|
| **Visual** | Zoom to 200%, check contrast, test color blindness sim |
| **Motor** | Keyboard-only navigation, touch target sizes |
| **Auditory** | Captions available, no audio-only info |
| **Cognitive** | Clear labels, consistent nav, error guidance |
| **Assistive Tech** | Screen reader walkthrough, switch control |

---

## Quick Reference

### Must Do (All Platforms)
- [ ] All interactive elements have accessible names
- [ ] All images have appropriate alt text
- [ ] Color contrast meets minimums (4.5:1 text, 3:1 UI)
- [ ] All functionality available via keyboard/assistive tech
- [ ] Touch targets meet minimum size (44×44)
- [ ] Text scales with user preference
- [ ] No color-only information
- [ ] Errors are clearly communicated
- [ ] Focus is visible and managed appropriately
- [ ] Motion can be reduced

### Should Do
- [ ] Logical heading hierarchy
- [ ] Clear landmarks/regions
- [ ] Consistent navigation
- [ ] Time limits can be extended
- [ ] No flashing content
- [ ] Help available for complex tasks
