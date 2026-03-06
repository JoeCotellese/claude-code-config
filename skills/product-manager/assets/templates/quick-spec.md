
# Quick Spec Template
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

**Accessibility**: [Tier 1 requirements - labels, tap targets, keyboard access]

---

## When to Use This Template

- Single user interaction
- Standard UX pattern (obvious how it works)
- Low risk (easy to revert if wrong)
- Can be documented in a ticket/issue directly
- No complex state management

## Template Sections Explained

### What
One clear sentence describing the user action and system response. Avoid jargon.

### Why
The user problem being solved. Not a business goal—focus on user value.

### Acceptance Criteria
3-5 testable conditions. Include:
- Happy path (core functionality)
- One edge case (boundary condition)
- One error state (what happens when things fail)

### Analytics
Single event with properties. Follow naming convention: `action_verb_noun`

### Accessibility
Minimum accessibility requirements. Reference platform-specific templates for details.
