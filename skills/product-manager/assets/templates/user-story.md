# ABOUTME: Generic user story template with acceptance criteria patterns.
# ABOUTME: Platform-agnostic structure; load platform-specific templates for examples.

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

### Accessibility Requirements
Define the accessibility tier and specific requirements:

**Tier**: [1-Required / 2-Expected / 3-Excellence]

| Requirement | Implementation |
|-------------|----------------|
| Screen reader labels | [List interactive elements and their labels] |
| Screen reader hints | [Hints for complex controls] |
| Text scaling | [How text scales at larger sizes] |
| Touch/click targets | [Confirm minimum size for all interactive elements] |
| Focus management | [Where focus moves after actions/navigation] |
| Motion preferences | [Alternative to animations, if any] |

**Accessibility Acceptance Criteria**:

- **Given** screen reader is enabled
  **When** user navigates to [element]
  **Then** screen reader announces "[label]" as a [button/link/etc.]

- **Given** text scaling is set to maximum
  **When** viewing this feature
  **Then** all text is legible and layout adapts without truncation

### Platform Considerations

- **Localization**: [Strings requiring translation, RTL considerations]
- **Privacy**: [Permissions needed, data collection disclosures]
- **Performance**: [Offline support, loading states, caching]

---

## Writing Guidelines

### Good User Stories

**Specific and testable:**
> As a returning customer, I want to see my recent orders on the home screen so that I can quickly reorder items.

**Bad - too vague:**
> As a user, I want a better experience.

### Acceptance Criteria Tips

1. **Start with the happy path** - What happens when everything works?
2. **Add edge cases** - What about empty states, boundaries, timeouts?
3. **Include error states** - What happens when things fail?
4. **Make them testable** - Can QA verify this passes/fails?

### Story Sizing

Stories should be:
- Implementable in 1-3 days
- Independently testable
- Valuable to the user on their own

If a story is too large, split it by:
- User action (search vs. filter vs. sort)
- Platform (mobile vs. desktop)
- Workflow step (create vs. edit vs. delete)
