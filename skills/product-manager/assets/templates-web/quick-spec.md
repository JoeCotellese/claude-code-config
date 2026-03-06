
# Quick Spec Template - Web Platforms
**Use for**: Single-interaction features, obvious UX, low risk. If you're debating whether
this needs a full brief, it probably doesn't.

---

## [Feature Name]

**What**: [One sentence — what does the user do and what happens?]

**Why**: [One sentence — what user problem does this solve?]

**Acceptance Criteria**:
- [ ] [Core behavior works]
- [ ] [Edge case handled]
- [ ] [Error state handled]

**Analytics**: `event_name` — [when it fires]

**Accessibility**:
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigable
- [ ] Screen reader announces state changes

---

## Examples

### Example 1: Copy to Clipboard

**What**: Click "Copy" button to copy API key to clipboard.

**Why**: Users want to quickly copy API keys without manual selection.

**Acceptance Criteria**:
- [ ] "Copy" button appears next to API key field
- [ ] Clicking shows "Copied!" confirmation for 2 seconds
- [ ] Works in all supported browsers (Chrome, Firefox, Safari, Edge)

**Analytics**: `api_key_copied` with `source: "dashboard"`

**Accessibility**:
- [ ] Button label: "Copy API key to clipboard"
- [ ] Screen reader announces "API key copied to clipboard" on success
- [ ] Focus remains on button after click

---

### Example 2: Dark Mode Toggle

**What**: Toggle switch in header to switch between light and dark themes.

**Why**: Users want to reduce eye strain in low-light environments.

**Acceptance Criteria**:
- [ ] Toggle persists across sessions (localStorage)
- [ ] Respects system preference on first visit
- [ ] Transition animation < 300ms

**Analytics**: `theme_changed` with `theme: "dark" | "light"`

**Accessibility**:
- [ ] ARIA: `role="switch"` with `aria-checked`
- [ ] Label: "Dark mode"
- [ ] Keyboard: Space/Enter toggles

---

### Example 3: Inline Edit Field

**What**: Click on project name to edit it inline.

**Why**: Reduce clicks for common rename operation.

**Acceptance Criteria**:
- [ ] Click transforms text into input field
- [ ] Enter saves, Escape cancels
- [ ] Shows spinner during save, error message if fails

**Analytics**: `project_renamed` with `project_id`

**Accessibility**:
- [ ] Focus moves to input on edit
- [ ] Screen reader announces "Editing project name"
- [ ] Error states announced via `aria-live`

---

### Example 4: Toast Notification Dismiss

**What**: Click X or wait 5 seconds to dismiss toast notification.

**Why**: Users want control over notification visibility.

**Acceptance Criteria**:
- [ ] Toast auto-dismisses after 5 seconds
- [ ] X button dismisses immediately
- [ ] Multiple toasts stack vertically

**Analytics**: `toast_dismissed` with `type`, `method: "manual" | "auto"`

**Accessibility**:
- [ ] `role="alert"` for important messages
- [ ] Dismiss button has label "Dismiss notification"
- [ ] Respects `prefers-reduced-motion` (no slide animation)
