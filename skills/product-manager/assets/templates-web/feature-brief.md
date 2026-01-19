# ABOUTME: Web-specific feature brief template with SaaS/web app examples.
# ABOUTME: Use for medium-complexity features on web platforms.

# [Feature Name] - Feature Brief (Web)

**Quick reference for lightweight feature planning. Use PRD template for complex features.**

---

## Summary

**What**: [One sentence describing the feature]

**Why**: [Primary business/user value]

**Who**: [Target user segment]

**Priority**: [P0-Critical / P1-High / P2-Medium / P3-Low]

---

## Objectives

### User Objective
[What problem does this solve for users?]

### Business Objective
[What business goal does this achieve?]

### Success Metric
[One key metric that defines success]
- Target: [Specific goal]

---

## User Experience

### Happy Path
1. User [action 1]
2. App [response 1]
3. User [action 2]
4. App [response 2]
5. Result: [outcome]

### Key Interactions
- **Primary Action**: [What the user does]
- **Visual Feedback**: [What the user sees]
- **Confirmation**: [How success is communicated]

---

## Web Platform Considerations

### Responsive Design
- **Mobile** (< 768px): [Layout/behavior]
- **Tablet** (768-1024px): [Layout/behavior]
- **Desktop** (> 1024px): [Layout/behavior]

### Browser Support
- Chrome: [Latest - N versions]
- Firefox: [Latest - N versions]
- Safari: [Latest - N versions]
- Edge: [Latest - N versions]

### Performance
- [ ] Core Web Vitals targets met (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Works on 3G connection
- [ ] Progressive enhancement for JavaScript-disabled

### SEO (if applicable)
- [ ] Semantic HTML structure
- [ ] Meta tags / Open Graph
- [ ] Server-side rendering or pre-rendering

---

## Technical Notes

### Requirements
- [API/service needed]
- [Framework/library - React, Vue, etc.]
- [Third-party integrations]

### Constraints
- [Browser limitations]
- [Performance requirements]
- [Offline/PWA behavior]

---

## Analytics

### Track These Events
- `event_name` - [When it fires]
- `event_name` - [When it fires]

### Monitor This Metric
[Primary success metric and how to measure it]

### Privacy Compliance
- [ ] Cookie consent obtained before tracking
- [ ] GDPR/CCPA compliant data collection
- [ ] User can opt-out

---

## Accessibility (WCAG 2.1 AA)

- [ ] **Keyboard**: All functionality accessible via keyboard
- [ ] **Focus**: Visible focus indicators, logical tab order
- [ ] **Screen Reader**: ARIA labels, live regions for dynamic content
- [ ] **Color**: 4.5:1 contrast ratio, no color-only information
- [ ] **Motion**: Respects `prefers-reduced-motion`
- [ ] **Zoom**: Content readable at 200% zoom

---

## Done When

- [ ] Core functionality works in all supported browsers
- [ ] Mobile responsive design implemented
- [ ] WCAG 2.1 AA compliance verified
- [ ] Analytics implemented
- [ ] Tested in staging environment

---

## Risks

| Risk | Mitigation |
|------|------------|
| Browser compatibility issue | [Cross-browser testing plan] |
| Performance regression | [Performance budget enforcement] |

---

## Example: Team Invitation Flow

### Summary

**What**: Invite team members via email to join workspace.

**Why**: Enable collaboration by allowing users to grow their team.

**Who**: Workspace admins and owners.

**Priority**: P1-High

### Objectives

**User Objective**: Quickly add colleagues to collaborate on projects.

**Business Objective**: Increase seats per workspace, driving revenue.

**Success Metric**: Invitation acceptance rate
- Target: > 60% of invitations accepted within 7 days

### User Experience

**Happy Path**:
1. User clicks "Invite Team" button
2. Modal opens with email input field
3. User enters email(s), separated by commas
4. User clicks "Send Invitations"
5. Result: Invitees receive email, pending invitations shown in team list

### Web Platform Considerations

**Responsive Design**:
- Mobile: Full-screen modal, single-column layout
- Tablet: Centered modal, 500px width
- Desktop: Centered modal, 600px width

**Performance**:
- Debounce email validation (300ms)
- Optimistic UI update on send
- Background job for email delivery

### Accessibility

- [x] Modal traps focus, Escape closes
- [x] Email input has associated label
- [x] Error messages linked via `aria-describedby`
- [x] Success announcement via `aria-live="polite"`
