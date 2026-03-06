
# Interaction Patterns
This reference covers common UI interaction patterns that apply across platforms. Platform-specific implementation details are noted where relevant.

---

## Navigation Patterns

### Tab Bar / Bottom Navigation

**Use When:**
- 3-5 top-level destinations
- Destinations are equally important
- User needs quick switching between sections

**Guidelines:**
- Keep to 3-5 items maximum
- Use icons + labels (icons alone are ambiguous)
- Indicate current selection clearly
- Persist across app (don't hide)
- Badge for notifications/counts

**Platform Notes:**
- iOS: Tab bar at bottom, always visible
- Android: Bottom navigation (Material)
- Web: Can be bottom on mobile, horizontal nav on desktop

### Hamburger Menu / Drawer

**Use When:**
- Many navigation destinations
- Secondary navigation
- Settings and account access

**Guidelines:**
- Use recognizable icon (three lines)
- Pair with label for accessibility
- Overlay on mobile, sidebar on desktop
- Show current location when open
- Easy dismiss (tap outside, swipe, X button)

**Caution:**
- Hamburger menus hide navigation; use tab bar when possible
- "Out of sight, out of mind" - hidden features get less use

### Breadcrumbs

**Use When:**
- Deep hierarchical structure
- Users may enter at any level
- Users need to navigate up hierarchy

**Guidelines:**
- Show path from root to current location
- Each level is clickable (except current)
- Current page not a link
- Use separator (/ or >)
- Truncate middle items on mobile if needed

### Hierarchical / Drill-Down

**Use When:**
- Content is organized hierarchically
- Each level reveals more detail
- Natural parent-child relationships

**Guidelines:**
- Clear back navigation
- Maintain context (where am I?)
- Consider breadcrumbs for deep hierarchies
- Show preview of what's at next level

**Platform Notes:**
- iOS: Navigation controller, push/pop
- Android: Up button in app bar
- Web: Browser back button, breadcrumbs

---

## List Patterns

### Basic List

**Use When:**
- Displaying items in sequence
- Items are similar in type
- Order may or may not matter

**Guidelines:**
- Clear visual separation between items
- Consistent item height (or clear variation)
- Tap/click anywhere on item for action
- Disclosure indicator for drill-down items

### Pull-to-Refresh

**Use When:**
- Content can be refreshed from server
- User-initiated update is natural
- Standard gesture is expected

**Guidelines:**
- Use standard animation/behavior
- Show loading indicator during refresh
- Update content in place when complete
- Handle errors gracefully (show message, keep old content)

**Platform Notes:**
- iOS: Standard UIRefreshControl
- Android: SwipeRefreshLayout
- Web: Custom implementation needed

### Infinite Scroll / Load More

**Use When:**
- Large datasets
- Content exploration (browsing, feeds)
- Pagination would interrupt flow

**Guidelines:**
- Load before user reaches bottom
- Show loading indicator at bottom
- Handle end of content gracefully
- Provide "Back to top" for long lists
- Preserve scroll position on back navigation

**Accessibility Concern:**
- Infinite scroll can trap keyboard users
- Provide alternative (pagination or "Load more" button)

### Swipe Actions

**Use When:**
- Quick actions on list items
- Actions are common and frequent
- Space is limited for action buttons

**Guidelines:**
- Destructive actions on trailing/right side
- Constructive actions on leading/left side
- Limit to 2-3 actions per side
- Provide alternative access (long press, context menu)
- Use clear icons and labels

**Platform Notes:**
- iOS: Standard swipe actions in lists
- Android: Similar, less standardized
- Web: Harder to discover, provide alternatives

---

## Form Patterns

### Single Column Forms

**Use When:**
- Mobile screens
- Linear completion flow
- Simple forms

**Guidelines:**
- One input per row
- Labels above inputs
- Clear visual grouping of related fields
- Progress indicator for long forms

### Inline Validation

**Use When:**
- Input has specific format requirements
- Immediate feedback is helpful
- User can fix errors right away

**Guidelines:**
- Validate on blur (not keystroke)
- Show success state for valid inputs
- Error message below field
- Don't validate empty optional fields

### Error Handling

**Guidelines:**
- Show errors near the field (not just at top)
- Use color + icon + text (not color alone)
- Explain what's wrong and how to fix
- Focus first error field
- Announce errors to screen readers

**Error Message Pattern:**
- Bad: "Invalid email" (what's wrong?)
- Good: "Please enter a valid email address, like name@example.com"

### Progressive Disclosure

**Use When:**
- Some fields are rarely needed
- Form would otherwise be overwhelming
- Advanced options for power users

**Guidelines:**
- Show common fields by default
- "Advanced options" or "More options" to reveal
- Remember user's preference (optional)
- Keep revealed fields visible once shown

### Multi-Step Forms (Wizards)

**Use When:**
- Long forms (10+ fields)
- Logical groupings of steps
- Conditional sections
- Complex processes

**Guidelines:**
- Show progress indicator
- Allow back navigation
- Save state between steps
- Validate before proceeding
- Summary/review step before final submission

---

## Modal Patterns

### When to Use Modals

**Good Uses:**
- Focused task requiring attention
- Confirmation of destructive action
- Critical information requiring acknowledgment
- Quick creation of simple item

**Bad Uses:**
- Long forms (use full page)
- Content browsing
- Information that could be inline
- Nested modals (never do this)

### Modal Sizes

| Size | Use Case |
|------|----------|
| **Small** | Confirmations, simple alerts |
| **Medium** | Short forms, quick creation |
| **Large** | Complex content, detailed info |
| **Full screen** | Mobile, or desktop when immersive |

### Sheets vs Modals

**Sheet (iOS) / Bottom Sheet (Android):**
- Slides from bottom
- Half-screen by default, expandable
- Good for quick tasks, options
- Can be dismissed by swiping down

**Modal / Dialog:**
- Centered overlay
- Fixed size (responsive)
- For focused attention
- Dismiss via button or escape

### Modal Accessibility

**Requirements:**
- Focus moves into modal when opened
- Focus trapped inside modal while open
- Escape key closes modal
- Focus returns to trigger when closed
- Background content is inert

---

## Search Patterns

### Search Bar Placement

| Position | Platform/Context |
|----------|------------------|
| **Top of screen** | iOS (in nav bar), Android, Web |
| **Expandable icon** | Space-constrained headers |
| **Persistent sidebar** | Desktop apps with frequent search |

### Search Experience

**Instant Search:**
- Results update as user types
- Debounce requests (200-300ms)
- Show loading state
- Clear previous results during loading

**Traditional Search:**
- Submit button or Enter to search
- Search results on separate view
- Clear query display on results page

### Search Suggestions

**Types:**
- Recent searches (user's history)
- Popular searches (trending)
- Autocomplete (predictive)
- Scoped suggestions (category + term)

**Guidelines:**
- Limit to 5-8 suggestions
- Show source of suggestion (icon for recent vs trending)
- Keyboard navigation through suggestions
- Tapping suggestion executes search

### No Results State

**Guidelines:**
- Confirm what was searched
- Offer suggestions for better results
- Check for typos
- Suggest related content
- Don't leave completely empty

---

## Action Patterns

### Confirmation for Destructive Actions

**Always confirm:**
- Permanent deletion
- Account termination
- Data loss
- Irreversible changes

**Confirmation Guidelines:**
- State what will happen clearly
- Name the specific item being affected
- Primary button is cancel (safe default)
- Destructive button is visually distinct
- Require explicit action (not auto-timed)

### Undo Pattern

**Use When:**
- Action is reversible
- Quick recovery is valuable
- Reduces need for confirmation

**Guidelines:**
- Toast/snackbar with undo action
- Time-limited (5-10 seconds)
- Prominent placement
- Clear labeling

### Loading States

**Types:**
- **Spinner**: Indeterminate, short waits
- **Skeleton**: Content placeholder, improves perceived speed
- **Progress bar**: Determinate, shows completion %
- **Button loading**: Replaces button text, disables

**Guidelines:**
- Show loading within 100ms
- Use skeleton for initial page load
- Progress bar for known duration operations
- Don't block entire UI if not necessary

---

## Empty States

### Purpose
Empty states are opportunities, not dead ends.

### Components
1. **Illustration** (optional): Friendly visual
2. **Headline**: What this area is for
3. **Description**: Why it's empty
4. **Action**: How to add content

### Examples by Context

| Context | Empty State |
|---------|-------------|
| First use | Welcome + getting started action |
| No search results | Suggestions for better search |
| Completed tasks | Celebration + what's next |
| No content yet | How to create first item |
| Error state | What went wrong + recovery |

### Guidelines
- Be helpful, not just decorative
- Provide clear next action
- Maintain brand voice
- Keep illustrations consistent with app style

---

## Gesture Reference

### Standard Gestures

| Gesture | Common Action |
|---------|---------------|
| **Tap** | Select, activate |
| **Long press** | Context menu, drag mode |
| **Swipe horizontal** | Delete, archive, actions |
| **Swipe vertical** | Scroll, pull-to-refresh |
| **Pinch** | Zoom in/out |
| **Double tap** | Zoom, like, expand |
| **Drag** | Move, reorder |

### Gesture Guidelines
- Use standard gestures for standard actions
- Gestures are not discoverable; provide button alternatives
- Custom gestures need teaching
- Provide haptic feedback where appropriate (iOS)
