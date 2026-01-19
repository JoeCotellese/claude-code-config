# ABOUTME: Web-specific user story template with SaaS/web app examples.
# ABOUTME: Includes WCAG, responsive design, and web platform acceptance criteria.

# User Story Template - Web Platforms

## Basic Format

**As a** [user type / persona]
**I want** [goal / desire]
**So that** [benefit / value / reason]

---

## Extended Template with All Sections

### Story: [Concise title]

**As a** [user type]
**I want** [goal]
**So that** [benefit]

### Acceptance Criteria
Use Given/When/Then format for testable scenarios:

- **Given** [initial context / preconditions]
  **When** [action / event]
  **Then** [expected outcome]

- **Given** [initial context]
  **When** [action]
  **Then** [expected outcome]

### Analytics Events
Events to implement for tracking this story:

- `event_name_1` - Fires when [trigger description]
- `event_name_2` - Fires when [trigger description]

### Edge Cases & Error Handling
Scenarios outside the happy path:

| Scenario | Expected Behavior |
|----------|-------------------|
| [Edge case 1] | [How the system should respond] |
| [Error condition] | [Error message, fallback, recovery] |
| [Boundary case] | [Expected handling] |

### Technical Dependencies
Prerequisites for implementation:

- [API endpoint needed]
- [Framework / library required - React, Vue, etc.]
- [Other stories that must be completed first]
- [Third-party service integration]

### Accessibility Requirements (WCAG 2.1 AA)

| Requirement | Implementation |
|-------------|----------------|
| Keyboard access | [Tab order, focus management] |
| Screen reader | [ARIA labels, live regions] |
| Color contrast | [Confirm 4.5:1 ratio] |
| Focus indicators | [Visible focus styles] |
| Motion | [prefers-reduced-motion support] |
| Zoom | [Readable at 200% zoom] |

**Accessibility Acceptance Criteria**:

- **Given** user is navigating with keyboard only
  **When** user tabs through [component]
  **Then** focus order is logical and all actions are accessible

- **Given** user is using a screen reader
  **When** [state change occurs]
  **Then** screen reader announces "[announcement]"

### Web Platform Considerations

- **Responsive**: [Behavior at mobile/tablet/desktop breakpoints]
- **Browser Support**: [Any browser-specific considerations]
- **Performance**: [Loading states, optimistic updates, caching]
- **Offline**: [PWA behavior if applicable]

---

## Example: Dashboard Data Export

### Story: Export Dashboard Data to CSV

**As a** workspace admin
**I want** to export my dashboard data as a CSV file
**So that** I can analyze it in Excel or share it with stakeholders

### Acceptance Criteria

- **Given** I am viewing the dashboard with data
  **When** I click the "Export" button and select "CSV"
  **Then** a CSV file downloads containing all visible data columns

- **Given** I have applied filters to the dashboard
  **When** I export to CSV
  **Then** the export respects my current filter selections

- **Given** the export contains more than 10,000 rows
  **When** I initiate the export
  **Then** I see a progress indicator and the export completes in the background

### Analytics Events

- `export_initiated` - Fires when user clicks export (properties: format, row_count)
- `export_completed` - Fires when download starts (properties: format, row_count, duration_ms)
- `export_failed` - Fires on error (properties: format, error_type)

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| No data to export | Show message: "No data available. Adjust your filters and try again." |
| Export exceeds size limit | Show message: "Export is too large. Please narrow your date range." |
| Network error during export | Show retry option: "Export failed. Click to retry." |
| User navigates away | Continue export in background, show notification when complete |

### Technical Dependencies

- Backend: `GET /api/v1/dashboard/export?format=csv&filters=...`
- File generation service (async for large exports)
- Browser download API / Blob handling

### Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| Keyboard access | Export button in tab order, dropdown navigable with arrows |
| Screen reader | "Export menu, expanded" when open, "Downloading CSV" announced |
| Focus indicators | Clear focus ring on export button and menu items |
| Motion | No animations in menu |

**Accessibility Acceptance Criteria**:

- **Given** user is using keyboard navigation
  **When** user focuses export button and presses Enter
  **Then** export menu opens and focus moves to first option

- **Given** screen reader is active
  **When** export download begins
  **Then** screen reader announces "Downloading dashboard data as CSV"

### Web Platform Considerations

- **Responsive**: On mobile, export menu displays as bottom sheet
- **Performance**: Large exports use streaming to avoid memory issues
- **Browser Support**: Uses download attribute (polyfill for older Safari)

---

## Example: SaaS Onboarding Checklist

### Story: Display Onboarding Progress Checklist

**As a** new user
**I want** to see a checklist of setup steps
**So that** I know what to do next and can track my progress

### Acceptance Criteria

- **Given** I am a new user who hasn't completed onboarding
  **When** I log in to the dashboard
  **Then** I see an onboarding checklist widget in the sidebar

- **Given** I complete a checklist item (e.g., "Invite a team member")
  **When** the action completes
  **Then** the checklist item shows as complete with a checkmark

- **Given** I have completed all checklist items
  **When** I view the dashboard
  **Then** the checklist is hidden and I see a "Setup complete!" celebration

### Analytics Events

- `onboarding_checklist_viewed` - Fires on first view (properties: items_complete, items_total)
- `onboarding_item_completed` - Fires per item (properties: item_name, time_since_signup)
- `onboarding_completed` - Fires when all done (properties: total_time, items_skipped)

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| User dismisses checklist | Hide with "Show setup guide" link in settings |
| Item completion fails | Keep item unchecked, show error toast |
| User is invited (not signed up) | Show simplified checklist (skip account setup items) |

### Technical Dependencies

- User onboarding state stored in user profile
- Real-time checklist updates via WebSocket or polling
- Celebration animation (confetti) - respect prefers-reduced-motion

### Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| Keyboard access | Checklist items focusable, Enter activates links |
| Screen reader | List with `role="list"`, completed items have `aria-checked="true"` |
| Motion | Celebration respects prefers-reduced-motion (static badge instead) |
| Contrast | Checkmarks and progress visible at 4.5:1 contrast |

### Web Platform Considerations

- **Responsive**: Checklist collapses to floating button on mobile
- **Performance**: Checklist state cached, updates debounced
- **Localization**: All checklist text translatable
