# ABOUTME: Visual design principles covering color, typography, spacing, and iconography.
# ABOUTME: Platform-agnostic guidance with accessibility considerations.

# Visual Design Principles

This reference covers foundational visual design principles that apply across platforms, with accessibility considerations throughout.

---

## Color Theory & Accessibility

### Color Purpose in UI

| Color Role | Purpose | Example |
|------------|---------|---------|
| **Primary** | Brand identity, main actions | Primary buttons, key elements |
| **Secondary** | Supporting elements | Secondary buttons, borders |
| **Accent** | Highlight, draw attention | CTAs, active states, links |
| **Background** | Surface colors | Page bg, card bg, modal bg |
| **Text** | Content colors | Primary, secondary, disabled text |
| **Semantic** | Meaning-bearing | Success (green), error (red), warning (yellow) |

### Contrast Requirements

| Content Type | WCAG AA | WCAG AAA |
|--------------|---------|----------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18pt+ or 14pt bold) | 3:1 | 4.5:1 |
| UI components & graphics | 3:1 | 3:1 |

### Creating Accessible Palettes

**Steps:**
1. Choose base brand colors
2. Generate tints/shades (50-900 scale)
3. Test combinations for contrast
4. Create semantic color mappings
5. Test in light and dark modes

**Tint/Shade Scale:**
```
50:  Lightest (backgrounds)
100: Light
200:
300:
400:
500: Base color
600:
700:
800:
900: Darkest (text on light bg)
```

### Color Blindness Considerations

**Avoid relying on:**
- Red/green distinction alone
- Hue as only differentiator
- Saturated colors without luminance contrast

**Safe distinctions:**
- Blue vs orange
- Add patterns, shapes, or labels
- Ensure luminance contrast

### Dark Mode Colors

**Key differences:**
- Don't just invert colors
- Use "elevated" surfaces (slightly lighter grays)
- Reduce saturation of bright colors
- Test contrast in both modes

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary bg | White (#FFFFFF) | Near black (#121212) |
| Elevated | Light gray | Dark gray (#1E1E1E) |
| Primary text | Black (#000000) | White (#FFFFFF) |
| Accent | Full saturation | Slightly desaturated |

---

## Typography Hierarchy

### Type Scale

A harmonious type scale creates visual hierarchy. Common scale ratio is 1.25 (Major Third):

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Display | 48-64px | Light-Regular | 1.1-1.2 |
| H1 | 32-40px | Regular-Medium | 1.2-1.3 |
| H2 | 24-28px | Medium | 1.3 |
| H3 | 20-22px | Medium | 1.3-1.4 |
| H4 | 18px | Semibold | 1.4 |
| Body | 16px | Regular | 1.5 |
| Small | 14px | Regular | 1.4 |
| Caption | 12px | Regular | 1.4 |

### Typography Best Practices

**Line Length:**
- Optimal: 50-75 characters per line
- Minimum: 45 characters
- Maximum: 90 characters
- Adjust column width, not font size

**Line Height:**
- Body text: 1.4-1.6 x font size
- Headings: 1.1-1.3 x font size
- Tight line height for large display type
- Looser for small/body text

**Font Weight:**
- Don't use more than 3 weights
- Contrast between heading and body weight
- Avoid light weights for small text
- Bold for emphasis, not size increase

### Text Accessibility

**Dynamic Type (iOS) / Browser Zoom (Web):**
- Text must scale with user preference
- Use relative units (rem, em, %) not px
- Test at 200% minimum
- Layouts should reflow, not just clip

**Readable Fonts:**
- Avoid overly decorative fonts for body text
- Ensure letters are distinguishable (Il1, O0)
- Consider dyslexia-friendly options (OpenDyslexic)
- Test with actual users

---

## Spacing Systems

### The 8pt Grid

Most design systems use multiples of 8:
- **4px**: Minimum spacing (subtle adjustments)
- **8px**: Base unit
- **16px**: Standard element spacing
- **24px**: Section separation
- **32px**: Major section breaks
- **48px, 64px, 96px**: Page-level spacing

**Why 8pt?**
- Divisible by 2, 4, 8 (works at various densities)
- Aligns well with common screen densities
- Creates consistent rhythm

### Spacing Application

| Context | Spacing |
|---------|---------|
| Icon to text | 8px |
| Between form fields | 16-24px |
| Card internal padding | 16-24px |
| Between cards | 16-24px |
| Section margins | 32-48px |
| Page margins (mobile) | 16px |
| Page margins (desktop) | 24-64px |

### Whitespace Principles

**Purpose of whitespace:**
- Creates breathing room
- Groups related content
- Signals hierarchy
- Improves readability

**Common mistakes:**
- Too little padding (cramped)
- Inconsistent spacing
- Different margins between similar elements
- Ignoring optical alignment

### Density Considerations

| Density | When to Use |
|---------|-------------|
| **Compact** | Data-dense UIs, dashboards, power users |
| **Default** | General purpose, balanced |
| **Comfortable** | Touch-first, accessibility, readability focus |

---

## Iconography

### Icon Styles

| Style | Character | Best For |
|-------|-----------|----------|
| **Outlined** | Light, modern | iOS, minimal UIs |
| **Filled** | Bold, emphatic | Selected states, emphasis |
| **Two-tone** | Decorative | Marketing, illustrations |
| **Duotone** | Layered | Modern web apps |

### Icon Guidelines

**Sizing:**
- Touch targets: 24x24px icon, 44x44px hit area
- Match icon optical size (some icons appear larger)
- Use consistent sizes within a context
- Common sizes: 16, 20, 24, 32, 48px

**Visual Weight:**
- Match icon weight to adjacent text weight
- SF Symbols: Use weight matching system
- Filled icons are visually heavier

**Meaning:**
- Use universally understood icons
- When in doubt, add a label
- Test with users; icons are often misunderstood
- Be consistent (same icon = same action)

### Platform Icon Systems

| Platform | System |
|----------|--------|
| iOS/macOS | SF Symbols (700+ icons) |
| Android | Material Icons |
| Web | Various: Heroicons, Feather, FontAwesome |

**SF Symbols Guidelines (Apple):**
- Prefer SF Symbols for system-like actions
- Match symbol weight to font weight
- Use rendering modes appropriately
- Customize only when necessary

---

## Visual Hierarchy

### Establishing Hierarchy

**Size:** Larger = more important
**Weight:** Bolder = more important
**Color:** More saturated/contrasting = more attention
**Space:** More whitespace = more importance
**Position:** Top/left (LTR) = higher priority

### Z-Pattern & F-Pattern

**F-Pattern:**
- Users scan in F-shape on text-heavy pages
- Put important content in first two paragraphs
- Use headings and bullets

**Z-Pattern:**
- Users scan in Z on image-heavy pages
- Logo top-left, CTA top-right or bottom-right
- Guide eye along the Z

### Visual Weight Balance

Elements have visual weight based on:
- Size
- Color darkness/saturation
- Density/complexity
- Isolation (surrounded by whitespace)

Balance the page so it doesn't feel lopsided.

---

## Consistency Principles

### Design Tokens

Use design tokens for consistent values:

```css
/* Spacing */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;

/* Colors */
--color-primary: #0066cc;
--color-text-primary: #1a1a1a;
--color-bg-primary: #ffffff;

/* Typography */
--font-size-body: 16px;
--font-size-heading: 24px;
--line-height-body: 1.5;
```

### Component Consistency

- Same component = same appearance
- Same action = same visual treatment
- Same meaning = same color
- Consistent spacing, alignment, sizing

### Pattern Library Benefits

- Faster design and development
- Consistent user experience
- Easier maintenance
- Reduced decision fatigue

---

## Responsive Visual Design

### Scaling Considerations

| Property | Mobile | Desktop |
|----------|--------|---------|
| Base font | 16px | 16px (same) |
| Heading sizes | Slightly smaller | Full scale |
| Touch targets | 44px min | 32px acceptable |
| Margins | 16px | 24-64px |
| Line length | Natural width | Constrain to 75 chars |

### Adaptive Typography

```css
/* Fluid typography example */
html {
    font-size: clamp(16px, 1vw + 14px, 20px);
}

h1 {
    font-size: clamp(1.75rem, 3vw + 1rem, 3rem);
}
```

### Image Considerations

- Provide multiple resolutions (@1x, @2x, @3x for iOS)
- Use responsive images (srcset)
- Lazy load below-fold images
- Optimize file sizes
- Consider aspect ratio containers

---

## Quick Reference

### Essential Checks

- [ ] Contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Text scales to 200% without breaking
- [ ] Color is not the only indicator
- [ ] Touch targets are 44x44 minimum
- [ ] Spacing is consistent (8pt grid)
- [ ] Typography hierarchy is clear
- [ ] Icons have labels or are universally understood
- [ ] Works in both light and dark mode
