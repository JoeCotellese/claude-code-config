# ABOUTME: Web platform UX reference covering WCAG 2.1, responsive design, and component patterns.
# ABOUTME: Includes accessibility requirements, breakpoints, focus management, and common UI patterns.

# Web Platform UX Reference

This reference covers web-specific UX patterns including WCAG 2.1 accessibility, responsive design, component guidelines, and interaction patterns for modern web applications.

---

## WCAG 2.1 Summary

### Conformance Levels

| Level | Description | Typical Requirement |
|-------|-------------|---------------------|
| **A** | Minimum accessibility | Basic functionality accessible |
| **AA** | Standard compliance | **Most common target**; meets legal requirements |
| **AAA** | Enhanced accessibility | Specialized contexts; difficult site-wide |

**Target Level AA for most projects.**

---

## Color Contrast Requirements

### Text Contrast Ratios

| Element | Minimum Ratio | Level |
|---------|---------------|-------|
| Normal text (< 18pt) | 4.5:1 | AA |
| Large text (≥ 18pt or 14pt bold) | 3:1 | AA |
| Normal text (enhanced) | 7:1 | AAA |
| Large text (enhanced) | 4.5:1 | AAA |
| UI components & graphics | 3:1 | AA |

### Testing Tools
- WebAIM Contrast Checker
- Chrome DevTools Color Picker
- Figma contrast plugins
- axe DevTools browser extension

### Common Issues
- Light gray text on white backgrounds
- Colored text on colored backgrounds
- Placeholder text with insufficient contrast
- Disabled states still need to be perceivable

---

## Keyboard Navigation

### Requirements
- **All functionality available via keyboard**
- **No keyboard traps** - User can always navigate away
- **Visible focus indicators** - Know what's focused
- **Logical tab order** - Matches visual order
- **Skip links** - Jump to main content

### Focus Indicators

```css
/* Default browser focus is acceptable but can be enhanced */
:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
}

/* NEVER do this without a replacement */
:focus { outline: none; } /* BAD */

/* Better: customize but maintain visibility */
:focus-visible {
    outline: 2px solid var(--focus-color);
    outline-offset: 2px;
}
```

### Skip Links
```html
<a href="#main-content" class="skip-link">Skip to main content</a>
<!-- Navigation here -->
<main id="main-content">
    <!-- Content here -->
</main>
```

### Key Behaviors

| Key | Expected Behavior |
|-----|-------------------|
| Tab | Move to next focusable element |
| Shift+Tab | Move to previous focusable element |
| Enter | Activate buttons, links |
| Space | Activate buttons, toggle checkboxes |
| Escape | Close modals, dismiss overlays |
| Arrow keys | Navigate within widgets (tabs, menus) |

---

## Focus Management

### When to Manage Focus
- **Modal opens**: Move focus into modal
- **Modal closes**: Return focus to trigger element
- **Content updates**: Announce or focus new content
- **Page navigation (SPA)**: Focus main content area
- **Form errors**: Focus first error field

### ARIA Live Regions
```html
<!-- For dynamic status updates -->
<div aria-live="polite" aria-atomic="true">
    <!-- Content changes announced to screen readers -->
</div>

<!-- For urgent updates -->
<div aria-live="assertive">
    <!-- Interrupts current announcement -->
</div>
```

---

## Responsive Design Patterns

### Standard Breakpoints

| Breakpoint | Width | Common Devices |
|------------|-------|----------------|
| Mobile | < 768px | Phones |
| Tablet | 768px - 1024px | Tablets, small laptops |
| Desktop | > 1024px | Laptops, monitors |
| Large | > 1440px | Large monitors |

### Mobile-First Approach
```css
/* Base styles for mobile */
.component {
    flex-direction: column;
}

/* Enhance for larger screens */
@media (min-width: 768px) {
    .component {
        flex-direction: row;
    }
}
```

### Common Patterns

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Reflow** | Single column mobile, multi-column desktop | Most content |
| **Off-canvas** | Navigation slides in from edge | Complex navigation |
| **Priority+** | Important items visible, others in "More" | Toolbars, tabs |
| **Stack** | Horizontal → vertical on small screens | Cards, forms |

---

## Touch & Click Targets

### Minimum Sizes
- **44x44px** - Apple recommendation
- **48x48px** - Google/Android recommendation
- **Use the larger (48px)** for better usability

### Spacing
- **8px minimum** between adjacent targets
- **16px recommended** for error prevention

### Considerations
- Visual size can be smaller than tap area
- Use padding to increase hit area without visual bloat
- Links in text: add vertical padding for mobile

---

## Component Guidelines

### Buttons

| Type | Use For | Visual Treatment |
|------|---------|-----------------|
| Primary | Main action (1 per view) | Filled, prominent color |
| Secondary | Alternative actions | Outlined or subtle fill |
| Tertiary | Less important actions | Text-only or minimal |
| Destructive | Delete, remove, cancel | Red/warning color |
| Disabled | Unavailable action | Reduced opacity, no interaction |

**Button Best Practices:**
- Use verbs: "Save changes" not "Submit"
- Be specific: "Delete account" not "Delete"
- Loading states: Show spinner, disable interaction
- Minimum width for touch: Full-width on mobile

### Forms

**Labels:**
- Always visible (not just placeholders)
- Associated with input via `for`/`id`
- Above or left of input (above preferred for mobile)

**Error Handling:**
- Inline validation on blur
- Error messages below the field
- Use `aria-describedby` to associate errors
- Don't rely on color alone (use icons/text)

```html
<label for="email">Email address</label>
<input
    type="email"
    id="email"
    aria-describedby="email-error"
    aria-invalid="true"
>
<span id="email-error" class="error">
    Please enter a valid email address
</span>
```

**Form Layout:**
- Single column on mobile
- Group related fields
- Required indicator (asterisk or text)
- Clear button labels ("Create account" not "Submit")

### Modals / Dialogs

**Accessibility Requirements:**
- Focus trapped inside while open
- Escape key closes
- Focus returns to trigger on close
- Background content inert (`aria-hidden` or `inert`)

```html
<div
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
>
    <h2 id="dialog-title">Confirm deletion</h2>
    <!-- Dialog content -->
</div>
```

**UX Guidelines:**
- Use for focused tasks requiring attention
- Don't use for simple alerts (use toast/snackbar)
- Avoid nested modals
- Provide clear close affordance

### Navigation

**Primary Navigation:**
- Consistent location across pages
- Current page indicated
- Keyboard accessible
- Mobile: hamburger or bottom nav

**Hamburger Menu:**
- Use with recognizable icon (3 lines)
- Label with "Menu" for screen readers
- Animate open/close state
- Trap focus when open

**Breadcrumbs:**
```html
<nav aria-label="Breadcrumb">
    <ol>
        <li><a href="/">Home</a></li>
        <li><a href="/products">Products</a></li>
        <li aria-current="page">Widget</li>
    </ol>
</nav>
```

### Tables

**Data Tables:**
- Use `<th>` with `scope="col"` or `scope="row"`
- Caption or `aria-labelledby` for table purpose
- Responsive: horizontal scroll or card layout on mobile
- Sortable columns: indicate sort direction

```html
<table aria-labelledby="table-caption">
    <caption id="table-caption">Monthly sales data</caption>
    <thead>
        <tr>
            <th scope="col">Month</th>
            <th scope="col">Revenue</th>
        </tr>
    </thead>
    <!-- ... -->
</table>
```

---

## Micro-interactions

### Hover States
- Subtle visual change (background, shadow)
- Not essential for functionality (touch has no hover)
- Transition for smoothness: `transition: 0.15s ease`

### Loading States
- Skeleton screens for content areas
- Spinners for discrete actions
- Progress bars for multi-step processes
- Disable triggers to prevent double submission

### Toast / Snackbar
- Non-blocking notifications
- Auto-dismiss after 5-8 seconds
- Include dismiss button
- Use `aria-live="polite"` for announcements

---

## Review Severity Guidance

### Critical (Must Fix)
- No keyboard access to functionality
- Missing form labels
- Color-only information
- Contrast below 3:1 for important UI
- Keyboard traps
- No skip link on content-heavy pages

### Major (Should Fix)
- Focus indicators removed without replacement
- Missing alt text on meaningful images
- Poor mobile touch targets (< 44px)
- Form errors not associated with fields
- Missing ARIA landmarks
- Confusing tab order

### Minor (Consider Fixing)
- Slightly below 4.5:1 contrast
- Missing aria-describedby for hints
- Could improve semantic structure
- Animation without reduce-motion support
- Missing loading states

---

## Common ARIA Patterns

### Disclosure (Expand/Collapse)
```html
<button aria-expanded="false" aria-controls="panel">
    Show details
</button>
<div id="panel" hidden>
    Expanded content here
</div>
```

### Tabs
```html
<div role="tablist" aria-label="Settings">
    <button role="tab" aria-selected="true" aria-controls="panel-1">
        General
    </button>
    <button role="tab" aria-selected="false" aria-controls="panel-2">
        Security
    </button>
</div>
<div role="tabpanel" id="panel-1">...</div>
<div role="tabpanel" id="panel-2" hidden>...</div>
```

### Alert
```html
<div role="alert">
    Your session will expire in 5 minutes.
</div>
```

---

## Testing Checklist

### Automated Tools
- [ ] Lighthouse accessibility audit (target 90+)
- [ ] axe-core browser extension
- [ ] WAVE accessibility evaluator

### Manual Testing
- [ ] Keyboard-only navigation (entire user flow)
- [ ] Screen reader walkthrough (NVDA or VoiceOver)
- [ ] Zoom to 200% (no horizontal scroll)
- [ ] Check with browser extensions (color blindness simulation)
- [ ] Test on actual mobile device

### Specific Checks
- [ ] All images have appropriate alt text
- [ ] All form fields have labels
- [ ] All buttons have accessible names
- [ ] Focus visible on all interactive elements
- [ ] Modals trap focus correctly
- [ ] Skip link works
- [ ] Landmarks present (main, nav, etc.)

---

## Resources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [Inclusive Components](https://inclusive-components.design/)
- [Deque University](https://dequeuniversity.com/)
