# User Story Template

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
- [Framework / library required]
- [Other stories that must be completed first]
- [Third-party service integration]

### Platform-Specific Considerations
Apple platform requirements:

- **Accessibility**: [VoiceOver labels, Dynamic Type support, etc.]
- **Localization**: [Strings requiring translation, RTL considerations]
- **Privacy**: [Permissions needed, privacy label updates]
- **Performance**: [Offline support, loading states, caching]

---

## Example: Recipe Sharing Feature

### Story: Share Recipe to Social Media

**As a** home cook using the recipe app
**I want** to share a recipe to Instagram or Messages
**So that** I can recommend recipes to my friends and family

### Acceptance Criteria

- **Given** I am viewing a recipe detail page
  **When** I tap the share button
  **Then** I see the iOS share sheet with social media and messaging options

- **Given** I have selected Instagram from the share sheet
  **When** the share completes
  **Then** I see a success confirmation and the recipe link is posted

- **Given** I am viewing a recipe without an internet connection
  **When** I tap the share button
  **Then** I see an error message "No internet connection. Please try again later."

### Analytics Events

- `tapped_share_button` - Fires when user taps share icon on recipe detail (properties: recipe_id, recipe_category)
- `completed_share` - Fires when share completes successfully (properties: recipe_id, share_destination, method)
- `cancelled_share` - Fires when user dismisses share sheet without sharing (properties: recipe_id)

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| No internet connection | Show alert: "No internet connection. Please try again later." with "OK" button |
| User denies share permission | Show iOS system permission prompt, respect user choice |
| Share fails (API error) | Show alert: "Unable to share recipe. Please try again." with "Retry" and "Cancel" buttons |
| Recipe has no image | Share with placeholder image and recipe title/description |

### Technical Dependencies

- UIActivityViewController (iOS native share sheet)
- LinkPresentation framework for rich link previews
- Recipe API endpoint: `GET /recipes/{id}/share-metadata`
- Network reachability check before initiating share

### Platform-Specific Considerations

- **Accessibility**: Share button has VoiceOver label "Share recipe", hint "Opens share menu"
- **Localization**: Error messages translated, share text adapts to user language
- **Privacy**: No tracking of what service user shares to (privacy by default)
- **Performance**: Pre-generate share image for instant sharing, cache for 5 minutes
