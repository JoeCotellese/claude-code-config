# ABOUTME: Apple platform UX reference for iOS, iPadOS, macOS, watchOS, and tvOS.
# ABOUTME: Covers HIG principles, SF Symbols, device patterns, Dark Mode, and review severity guidance.

# Apple Platform UX Reference

This reference covers Apple Human Interface Guidelines (HIG) for designing native iOS, iPadOS, macOS, watchOS, and tvOS experiences.

---

## Design Principles

Apple's design philosophy rests on three pillars:

### Clarity
- Content is paramount; design supports rather than competes
- White space gives content room to breathe
- Typography is legible and purposeful
- Icons are precise and comprehensible

### Deference
- The interface recedes to showcase content
- Translucency hints at context and hierarchy
- Animation provides feedback without distraction
- System controls feel familiar and predictable

### Depth
- Distinct visual layers convey hierarchy
- Transitions animate between layers
- Touch gestures reveal hidden layers
- Motion reinforces spatial relationships

---

## Platform-Specific Patterns

### iOS/iPadOS

| Pattern | Usage | Key Considerations |
|---------|-------|-------------------|
| **Navigation Bar** | Hierarchical navigation | Title, back button, optional right actions |
| **Tab Bar** | Top-level app sections (3-5 tabs) | Always visible, icons + labels, badge support |
| **Search Bar** | Content filtering/search | Large title collapse behavior |
| **Pull-to-Refresh** | Manual content update | Standard gesture, no custom animations |
| **Swipe Actions** | Quick item actions | Destructive actions on right, constructive on left |
| **Context Menus** | Long-press actions | Preview + actions, haptic feedback |
| **Sheets** | Modal content | Half-sheet for quick tasks, full for complex |

### iPadOS-Specific

| Pattern | Usage |
|---------|-------|
| **Split View** | Primary-detail interface (required for iPad) |
| **Sidebar** | App navigation (collapsible) |
| **Popovers** | Contextual options (vs. sheets on iPhone) |
| **Drag and Drop** | Cross-app content transfer |
| **Keyboard Shortcuts** | Power user acceleration |

### macOS-Specific

| Pattern | Usage |
|---------|-------|
| **Menu Bar** | App-level and system commands |
| **Toolbar** | Frequent document actions |
| **Sidebar** | Navigation and scope filtering |
| **Inspectors** | Property editing panels |
| **Sheets** | Document-modal dialogs |
| **Alerts** | App-modal confirmations |

### watchOS-Specific

| Pattern | Usage |
|---------|-------|
| **List** | Primary navigation pattern |
| **Detail View** | Single item with scroll |
| **Complications** | Glanceable watch face data |
| **Notifications** | Short Look / Long Look |
| **Digital Crown** | Precise scrolling input |

---

## SF Symbols

### Usage Guidelines
- **Prefer SF Symbols over custom icons** for system actions
- **Match weight to typography** (regular symbol with regular text)
- **Use rendering modes appropriately**:
  - Monochrome: Standard UI icons
  - Hierarchical: Depth and emphasis
  - Palette: Custom multi-color
  - Multicolor: System-defined colors (e.g., weather)

### Common Symbols

| Action | Symbol Name |
|--------|-------------|
| Share | `square.and.arrow.up` |
| Add | `plus` or `plus.circle` |
| Delete | `trash` |
| Edit | `pencil` or `square.and.pencil` |
| Settings | `gearshape` |
| Search | `magnifyingglass` |
| Close | `xmark` |
| Done/Check | `checkmark` |
| Favorite | `heart` / `heart.fill` |
| More Options | `ellipsis` |
| Refresh | `arrow.clockwise` |
| Filter | `line.3.horizontal.decrease` |

### Symbol Configuration
```swift
// Proper symbol configuration
Image(systemName: "star.fill")
    .symbolRenderingMode(.hierarchical)
    .font(.system(size: 17, weight: .regular))
```

---

## Dark Mode

### Requirements
- **Support is expected** - Users can enable Dark Mode system-wide
- **Use semantic colors** - Never hardcode light/dark values
- **Test both appearances** - Design must work in both modes

### Color Guidelines

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary background | White | System Black |
| Secondary background | System Gray 6 | System Gray 5 |
| Primary text | Black (label) | White (label) |
| Secondary text | Gray (secondaryLabel) | Gray (secondaryLabel) |
| Tint/accent | App tint color | Same, possibly adjusted for vibrancy |

### Common Issues
- Hardcoded colors that don't adapt
- Images with transparent backgrounds assuming white
- Insufficient contrast in Dark Mode
- Drop shadows that look wrong on dark backgrounds

### Best Practices
- Use `Color(.label)`, `Color(.secondaryLabel)`, etc.
- Use `Color(.systemBackground)`, `Color(.secondarySystemBackground)`
- Test with Increase Contrast enabled
- Provide Dark Mode variants for custom images

---

## Device Considerations

### iPhone

| Feature | Models | Design Impact |
|---------|--------|---------------|
| Dynamic Island | 14 Pro+ | Live Activities, compact/expanded states |
| Action Button | 15 Pro+ | Custom quick actions |
| Camera Control | 16+ | Hardware camera button integration |
| Face ID | X+ | Accommodate sensor housing |
| Home Indicator | X+ | Safe area at bottom |

### Screen Sizes (Points)

| Device | Width | Height |
|--------|-------|--------|
| iPhone SE | 375 | 667 |
| iPhone 14 | 390 | 844 |
| iPhone 14 Pro Max | 430 | 932 |
| iPad Mini | 744 | 1133 |
| iPad Pro 12.9" | 1024 | 1366 |

### Safe Areas
- Always use safe area insets
- Don't place interactive elements in unsafe areas
- Content can extend behind bars for visual effect

---

## Typography

### System Fonts

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Large Title | 34pt | Regular | Screen titles (scrollable) |
| Title 1 | 28pt | Regular | Prominent titles |
| Title 2 | 22pt | Regular | Section headers |
| Title 3 | 20pt | Regular | Subsection headers |
| Headline | 17pt | Semibold | Emphasized body |
| Body | 17pt | Regular | Primary content |
| Callout | 16pt | Regular | Secondary content |
| Subheadline | 15pt | Regular | Tertiary content |
| Footnote | 13pt | Regular | Fine print |
| Caption 1 | 12pt | Regular | Metadata |
| Caption 2 | 11pt | Regular | Smallest text |

### Dynamic Type Support
- **Required**: Text must scale with user preference
- **Test at largest accessibility sizes** (AX1-AX5)
- **Allow text truncation or wrapping** at extremes
- Use `@ScaledMetric` for custom spacing that scales

---

## Touch Targets

### Minimum Sizes
- **44x44 points** - Minimum tappable area (Apple requirement)
- **48x48 points** - Recommended for primary actions
- **Visual size can be smaller** but hit area must meet minimum

### Spacing
- **8 points minimum** between adjacent touch targets
- **16 points recommended** for error prevention

---

## Review Severity Guidance

When reviewing designs against HIG, use these severity levels:

### Critical (Must Fix)
Issues that will likely cause:
- App Store rejection
- App unusable for some users
- Significant accessibility barriers

Examples:
- No VoiceOver labels on interactive elements
- Touch targets below 44x44 points
- Color-only information conveyance
- Text that doesn't support Dynamic Type
- No Dark Mode support

### Major (Should Fix)
Issues that:
- Significantly degrade user experience
- Violate common HIG patterns
- Cause user confusion

Examples:
- Non-standard navigation patterns
- Missing haptic feedback on expected actions
- Inconsistent icon usage
- Poor contrast ratios
- Missing empty states

### Minor (Consider Fixing)
Issues that:
- Represent missed opportunities
- Minor polish improvements
- Subjective preference

Examples:
- Could use more appropriate SF Symbol
- Spacing slightly off from 4pt grid
- Animation timing could be refined
- Could add more VoiceOver hints

---

## Common HIG Violations

### Navigation
- Custom back buttons that break swipe-to-go-back
- Hiding the tab bar when it should remain visible
- Using hamburger menus instead of tab bars on iOS
- Modal sheets for content that should be pushed

### Interactions
- Custom pull-to-refresh animations
- Requiring long press without visual affordance
- Non-standard gesture recognizers
- Missing confirmation for destructive actions

### Visual Design
- Non-system fonts for UI chrome
- Custom segmented controls that don't match system
- Hardcoded colors that don't adapt to Dark Mode
- Icons that don't match SF Symbol style

### Accessibility
- Images without meaningful alt text
- Grouped content not grouped for VoiceOver
- Custom controls missing accessibility traits
- Animations without Reduce Motion alternatives

---

## MCP Integration

For authoritative HIG documentation, use the `apple-docs` MCP server:

```
1. choose_technology("Human Interface Guidelines")
2. search_symbols("navigation bars")
3. get_documentation("/documentation/...")
```

This provides the latest HIG guidance directly from Apple's documentation.

---

## Resources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SF Symbols App](https://developer.apple.com/sf-symbols/)
- [Apple Design Resources](https://developer.apple.com/design/resources/)
- [WWDC Design Videos](https://developer.apple.com/videos/design/)
