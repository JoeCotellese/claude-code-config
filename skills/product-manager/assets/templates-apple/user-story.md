
# User Story Template - Apple Platforms
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
- [Framework / library required - UIKit, SwiftUI, etc.]
- [Other stories that must be completed first]
- [Third-party service integration]

### Accessibility Requirements
Define the accessibility tier and specific requirements (see `references/platforms/apple.md`):

**Tier**: [1-Required / 2-Expected / 3-Excellence]

| Requirement | Implementation |
|-------------|----------------|
| VoiceOver labels | [List interactive elements and their labels] |
| VoiceOver hints | [Hints for complex controls] |
| Dynamic Type | [How text scales at accessibility sizes] |
| Tap targets | [Confirm 44pt minimum for all interactive elements] |
| Focus management | [Where focus moves after actions/navigation] |
| Reduce Motion | [Alternative to animations, if any] |

**Accessibility Acceptance Criteria**:

- **Given** VoiceOver is enabled
  **When** user navigates to [element]
  **Then** VoiceOver announces "[label]" as a [button/link/etc.]

- **Given** Dynamic Type is set to accessibility size
  **When** viewing this feature
  **Then** all text is legible and layout adapts without truncation

### Apple Platform Considerations

- **Localization**: [Strings requiring translation, RTL considerations]
- **Privacy**: [Permissions needed, privacy label updates]
- **Performance**: [Offline support, loading states, caching]
- **Widget/Extension**: [Does this affect widgets or extensions?]

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

### Accessibility Requirements

**Tier**: 1-Required

| Requirement | Implementation |
|-------------|----------------|
| VoiceOver labels | Share button: "Share recipe" |
| VoiceOver hints | Share button: "Opens share menu" |
| Dynamic Type | Error messages scale with system text size |
| Tap targets | Share button minimum 44x44pt |
| Focus management | Focus returns to recipe after share sheet dismisses |
| Reduce Motion | N/A (no custom animations) |

**Accessibility Acceptance Criteria**:

- **Given** VoiceOver is enabled
  **When** user navigates to the share button
  **Then** VoiceOver announces "Share recipe, button" with hint "Opens share menu"

- **Given** VoiceOver is enabled and share fails
  **When** the error alert appears
  **Then** VoiceOver announces the error message and focus moves to the alert

### Apple Platform Considerations

- **Localization**: Error messages translated, share text adapts to user language
- **Privacy**: No tracking of what service user shares to (privacy by default)
- **Performance**: Pre-generate share image for instant sharing, cache for 5 minutes
- **iPad**: Share sheet presents as popover from share button, not full screen

---

## Example: Siri Shortcut - Start Cooking

### Story: Voice-Activated Recipe Start

**As a** busy home cook
**I want** to say "Hey Siri, start cooking [recipe name]"
**So that** I can begin a recipe hands-free while prepping ingredients

### Acceptance Criteria

- **Given** I have added a recipe to my Shortcuts
  **When** I say "Hey Siri, start cooking Pasta Carbonara"
  **Then** the app opens to the recipe in step-by-step cooking mode

- **Given** I have multiple recipes with similar names
  **When** Siri can't determine which recipe
  **Then** Siri shows a disambiguation list to choose from

### Analytics Events

- `shortcut_invoked` - Fires when Siri opens app (properties: recipe_id, invocation_method: "siri")
- `cooking_mode_started` - Fires when step-by-step begins (properties: recipe_id, source: "shortcut")

### Technical Dependencies

- App Intents framework (iOS 16+)
- SiriKit donation for recipe shortcuts
- Indexed recipes via Spotlight/CoreSpotlight

### Accessibility Requirements

**Tier**: 2-Expected (Voice interface is inherently accessible)

| Requirement | Implementation |
|-------------|----------------|
| VoiceOver | Cooking mode fully accessible |
| Voice Control | All actions available via voice commands |
| Reduce Motion | Step transitions are instant |

### Apple Platform Considerations

- **Localization**: Intent phrases localized per language
- **Privacy**: Recipe names donated to Siri, disclosed in privacy policy
- **HomePod**: Works from HomePod, opens on nearby iOS device
