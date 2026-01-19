# ABOUTME: Web platform considerations for product managers.
# ABOUTME: Covers accessibility (WCAG), responsive design, PWA, SEO, SaaS patterns, and analytics.

# Web Platform Considerations

This reference covers web-specific product considerations including accessibility standards, responsive design, Progressive Web Apps, SEO, SaaS patterns, and analytics implementation.

---

## Accessibility (WCAG 2.1)

### WCAG Levels

| Level | Description | Typical Requirement |
|-------|-------------|---------------------|
| **A** | Minimum accessibility | Basic functionality accessible |
| **AA** | Standard compliance | **Most common target**; meets legal requirements |
| **AAA** | Enhanced accessibility | Specialized apps; difficult to achieve site-wide |

### Level AA Requirements (Target This)

**Perceivable**
- [ ] Text alternatives for images (alt text)
- [ ] Captions for video/audio
- [ ] Color contrast: 4.5:1 for normal text, 3:1 for large text
- [ ] Content readable without color
- [ ] Text resizable to 200% without loss of function

**Operable**
- [ ] All functionality via keyboard
- [ ] No keyboard traps
- [ ] Skip links for navigation
- [ ] Focus indicators visible
- [ ] No content that flashes more than 3x/second
- [ ] Page titles descriptive
- [ ] Focus order logical

**Understandable**
- [ ] Language of page specified
- [ ] Consistent navigation
- [ ] Consistent identification of elements
- [ ] Error identification in text
- [ ] Labels for form inputs
- [ ] Error suggestions provided

**Robust**
- [ ] Valid HTML
- [ ] Name, role, value for custom components
- [ ] Status messages announced (aria-live)

### ARIA Implementation Checklist

| Pattern | ARIA Attributes |
|---------|----------------|
| Landmarks | `role="main"`, `role="nav"`, `role="banner"`, `role="contentinfo"` |
| Buttons | Inherent with `<button>`; use `role="button"` for divs |
| Dialogs | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| Tabs | `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected` |
| Expandables | `aria-expanded`, `aria-controls` |
| Live regions | `aria-live="polite"` or `"assertive"` |
| Form errors | `aria-describedby`, `aria-invalid="true"` |

### Testing Tools
- **Automated**: Lighthouse, axe-core, WAVE
- **Manual**: Screen reader (NVDA, VoiceOver, JAWS), keyboard-only navigation
- **Simulation**: Color blindness simulators, zoom to 200%

### Legal Considerations
- ADA (US): Web accessibility lawsuits increasing
- Section 508: Federal agencies and contractors
- EN 301 549: European accessibility standard
- Risk: Lawsuits, settlements, reputation damage

---

## Responsive Design

### Standard Breakpoints

| Breakpoint | Width | Common Devices |
|------------|-------|----------------|
| Mobile | < 768px | Phones |
| Tablet | 768px - 1024px | Tablets, small laptops |
| Desktop | > 1024px | Laptops, monitors |
| Large | > 1440px | Large monitors |

### Mobile-First Approach
1. Design for smallest screen first
2. Add complexity via media queries (`min-width`)
3. Benefits: Forces prioritization, better performance on mobile

### Responsive Patterns

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Reflow** | Single column on mobile, multi-column on desktop | Most content |
| **Off-canvas** | Navigation hidden off-screen on mobile | Complex navigation |
| **Priority+** | Show important items, hide others in "More" menu | Toolbars, tabs |
| **Stack** | Horizontal → vertical on small screens | Cards, forms |

### Touch Considerations
- Minimum tap target: 44x44px (Apple), 48x48px (Google)
- Spacing between targets: 8px minimum
- Hover states don't work: Provide alternatives
- Swipe gestures: Not discoverable; provide button alternatives

---

## Progressive Web Apps (PWA)

### Core Technologies

| Technology | Purpose | Requirement |
|------------|---------|-------------|
| **Service Worker** | Offline support, caching, background sync | Required for PWA |
| **Web App Manifest** | Install prompt, home screen icon, theme | Required for PWA |
| **HTTPS** | Security requirement | Required |

### PWA Capabilities

| Capability | Support | Notes |
|------------|---------|-------|
| Offline access | Good | Via service worker caching |
| Push notifications | Good (not iOS Safari) | Requires user permission |
| Home screen install | Good | Varies by browser prompts |
| Background sync | Limited | Chrome/Edge only |
| File system access | Limited | Origin private file system |
| Bluetooth/USB | Limited | Chromium only |

### PWA vs Native App Decision

| Factor | PWA | Native App |
|--------|-----|------------|
| Distribution | Web URL, no app store | App store discovery |
| Install friction | Low (add to home screen) | Higher (app store download) |
| Updates | Instant | App store review cycle |
| Platform APIs | Limited | Full access |
| Monetization | No app store cut | 30/15% commission |
| Offline | Good with service worker | Excellent |

### When to Choose PWA
- Content-focused apps (news, recipes, documentation)
- Supplement to existing web app
- Markets with low app store penetration
- Need instant updates without app store review

---

## SEO Considerations

### Core Web Vitals (Ranking Factors)

| Metric | Target | Description |
|--------|--------|-------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | Time to render largest content |
| **FID** (First Input Delay) | < 100ms | Time to respond to first interaction |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Visual stability (no jumping content) |

### Technical SEO Checklist

**Crawlability**
- [ ] Robots.txt allows important pages
- [ ] XML sitemap submitted to search engines
- [ ] No broken internal links
- [ ] Canonical URLs specified

**Content**
- [ ] Descriptive page titles (< 60 chars)
- [ ] Meta descriptions (< 160 chars)
- [ ] Heading hierarchy (H1 > H2 > H3)
- [ ] Alt text for meaningful images
- [ ] Structured data (JSON-LD)

**Performance**
- [ ] Core Web Vitals passing
- [ ] Mobile-friendly (responsive)
- [ ] HTTPS enabled
- [ ] Fast time to first byte (< 200ms)

### Structured Data (JSON-LD)

Common schemas:
- `Organization`: Company info
- `Product`: E-commerce products
- `Article`: Blog posts, news
- `FAQ`: FAQ pages
- `BreadcrumbList`: Navigation trails
- `LocalBusiness`: Physical locations

### Single-Page App (SPA) SEO
- Server-side rendering (SSR) or pre-rendering for crawlability
- Dynamic rendering as fallback
- History API for proper URLs
- Meta tags updated per page

---

## SaaS Patterns

### Multi-Tenancy Models

| Model | Description | Trade-offs |
|-------|-------------|------------|
| **Shared database** | All tenants in one DB, tenant_id column | Simple; harder to scale/isolate |
| **Schema per tenant** | Same DB, separate schemas | Balance of isolation/complexity |
| **Database per tenant** | Fully separate databases | Best isolation; complex operations |

### Common SaaS Features

**User Management**
- Organizations / Workspaces
- Role-based access control (RBAC)
- Team invitations
- SSO / SAML integration (enterprise)

**Subscription & Billing**
- Plan tiers (Free, Pro, Enterprise)
- Usage-based billing
- Seat-based billing
- Trial periods
- Plan upgrades/downgrades

**Onboarding**
- First-run experience
- Empty states with guidance
- Checklists / progress indicators
- Tooltips / product tours

### Pricing Page Best Practices
- 3-4 tiers maximum
- Clear feature comparison
- Highlight recommended tier
- Annual discount incentive
- Free trial CTA prominent

### Trial Strategy

| Approach | Pros | Cons |
|----------|------|------|
| **Free trial** | Low friction, full experience | Tire-kickers, support cost |
| **Freemium** | Ongoing free users = marketing | Conversion optimization challenge |
| **Paid trial ($1)** | Qualifies serious users | Higher friction |

---

## Browser Support Strategy

### Evergreen Browser Policy
Support last 2 versions of:
- Chrome (desktop + Android)
- Firefox
- Safari (macOS + iOS)
- Edge

### Deciding on IE11 / Legacy Support
- Check actual analytics (what % of users?)
- B2B enterprise: May need IE11 longer
- B2C modern: Drop aggressively
- Cost: Polyfills, testing, limited features

### Feature Detection
```javascript
if ('IntersectionObserver' in window) {
  // Use native IntersectionObserver
} else {
  // Polyfill or fallback
}
```

### Polyfill Strategy
- Ship polyfills only to browsers that need them
- Use polyfill.io or similar service
- Prefer smaller, targeted polyfills over large bundles

---

## Analytics & Privacy

### Event Tracking Conventions

| Category | Pattern | Example |
|----------|---------|---------|
| Page views | `page_viewed` | `page_viewed` with `path: "/dashboard"` |
| User actions | `{action}_{object}` | `clicked_signup_button` |
| Conversions | `{goal}_completed` | `checkout_completed` |
| Errors | `{context}_error` | `form_validation_error` |

### Privacy Regulations

| Regulation | Scope | Key Requirements |
|------------|-------|------------------|
| **GDPR** | EU users | Consent, right to access/delete/port |
| **CCPA/CPRA** | California | "Do Not Sell" opt-out, disclosure |
| **ePrivacy** | EU | Cookie consent |

### Cookie Consent Implementation
- Banner with clear accept/reject options
- Granular controls (analytics, marketing, functional)
- No tracking before consent
- Remember preferences
- Easy to change preferences later

### Privacy-Respecting Analytics
- Aggregate, don't track individuals
- Anonymize IP addresses
- Short retention periods
- Consider privacy-focused tools (Plausible, Fathom)
- Respect DNT (Do Not Track) header

---

## Performance Budgets

### Recommended Targets

| Metric | Budget |
|--------|--------|
| JavaScript (gzipped) | < 200KB |
| CSS (gzipped) | < 50KB |
| Images (above fold) | < 200KB |
| Total page weight | < 1MB |
| Time to Interactive | < 3s on 3G |
| First Contentful Paint | < 1.5s |

### Performance Optimization Techniques
- Code splitting (load only what's needed)
- Lazy loading (images, below-fold content)
- CDN for static assets
- Image optimization (WebP, responsive images)
- Caching headers
- Compression (gzip/brotli)

---

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [web.dev](https://web.dev/) - Google's web best practices
- [MDN Web Docs](https://developer.mozilla.org/)
- [Can I Use](https://caniuse.com/) - Browser support tables
- [Schema.org](https://schema.org/) - Structured data vocabulary
