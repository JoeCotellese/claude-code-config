
# Apple Platform Considerations
This reference consolidates Apple-specific product considerations including platform capabilities, App Store guidelines, monetization strategies, accessibility requirements, and analytics implementation.

---

## Platform Capabilities

### iOS/iPadOS Specific

| Feature | Description | PM Considerations |
|---------|-------------|-------------------|
| **Widgets** | Home Screen, Lock Screen, StandBy mode | Glanceable info only; design for multiple sizes |
| **Live Activities** | Real-time updates on Lock Screen and Dynamic Island | Time-sensitive content (orders, sports, timers) |
| **App Clips** | Lightweight experiences without full install | Discovery and onboarding use cases |
| **Shortcuts** | Siri Shortcuts and automation | Power user retention; voice-first interactions |
| **Focus Filters** | App behavior in Focus modes | Respect user's intent to limit distractions |
| **Handoff** | Continuity between devices | Seamless cross-device journeys |

### Apple Ecosystem Integration

| Feature | Description | PM Considerations |
|---------|-------------|-------------------|
| **iCloud** | CloudKit for data sync, iCloud Drive for documents | User expects sync; plan for conflict resolution |
| **Sign in with Apple** | Privacy-focused authentication | Required if offering third-party auth options |
| **SharePlay** | Synchronized FaceTime experiences | Social features; shared viewing/activities |
| **AirDrop** | Peer-to-peer content sharing | Content sharing use cases |
| **Universal Clipboard** | Copy/paste between devices | Ecosystem stickiness |

### Device-Specific Features

**iPhone**
- Dynamic Island (14 Pro+): Compact/expanded states for ongoing activities
- Action Button (15 Pro+): Custom quick actions
- Camera Control (16+): Hardware camera button

**iPad**
- Split View / Slide Over: Multitasking support required
- Stage Manager: Windowed mode on supported devices
- Apple Pencil: Handwriting, drawing, annotation
- Trackpad/Keyboard: Desktop-class interactions

**Apple Watch**
- Always-on display: Persistent info without interaction
- Complications: Glanceable data on watch face
- Digital Crown: Precise scrolling input
- Background modes: Limited; plan for constraints

**Apple TV**
- Siri Remote: D-pad navigation, no touch screen
- Multi-user support: Profiles and personalization
- Picture in Picture: Background video playback

---

## App Store Guidelines Impact

### Common Rejection Reasons

| Guideline | Issue | Prevention |
|-----------|-------|------------|
| **2.1 - App Completeness** | Crashes, bugs, placeholder content | Thorough TestFlight testing |
| **4.3 - Spam** | Too similar to existing apps, repetitive | Clear differentiation |
| **5.1.1 - Privacy** | Missing privacy policy, improper data handling | Privacy review before submission |
| **2.3.10 - Accurate Metadata** | Misleading descriptions or screenshots | Honest marketing |
| **3.1.1 - In-App Purchase** | Using non-IAP payment for digital goods | Understand IAP requirements |

### Business Model Constraints

| Content Type | Payment Rule |
|--------------|--------------|
| Digital goods/services | Must use In-App Purchase (30/15% commission) |
| Physical goods/services | Can use external payment processors |
| Reader apps | Can link to external subscription management |
| External links | New rules allow limited linking out (with entitlement) |

### App Review Notes
- Include clear demo instructions for reviewers
- Provide test account if login required
- Explain any unusual features or permissions
- Allow 1-3 days for standard review

---

## Monetization Strategy

### In-App Purchase (IAP) vs Subscription

**Choose IAP when:**
- Content is consumable (coins, power-ups)
- One-time feature unlocks (remove ads, pro features)
- Content packs or expansions
- User prefers one-time purchase

**Choose Subscription when:**
- Ongoing service or content updates
- Regular operational costs (server, API, content)
- Want predictable recurring revenue
- Offering tiered access levels

### Comparison

| Factor | IAP | Subscription |
|--------|-----|--------------|
| Revenue predictability | Low | High |
| User friction | Lower (one-time) | Higher (recurring commitment) |
| Lifetime value | Lower | Higher |
| Pricing flexibility | Fixed after purchase | Can adjust over time |
| User expectation | Pay once, own forever | Continuous value delivery |

### Freemium vs Paid Upfront vs Trial

| Model | Best For | Typical Conversion |
|-------|----------|-------------------|
| **Freemium** | Social apps, content platforms, utilities | 2-5% |
| **Paid Upfront** | Professional tools, specialized apps | N/A (pre-purchase decision) |
| **Free Trial** | Subscription apps, complex products | 10-30% (trial to paid) |

### Subscription Considerations
- **Pricing Tiers**: Use Apple's predefined price points
- **Introductory Offers**: Free trials, pay-up-front, pay-as-you-go
- **Family Sharing**: Automatic for most subscriptions
- **Refund Windows**: Customer refund policies affect retention metrics

---

## Version and Device Support

### iOS Version Strategy

| Strategy | Version | Trade-off |
|----------|---------|-----------|
| Latest only | iOS 18+ | Newest features, smallest audience |
| Latest - 1 | iOS 17+ | Balance of features and reach |
| Latest - 2 | iOS 16+ | Broader reach, older APIs |

**Typical support**: Latest 2-3 major iOS versions

### Device Compatibility Decisions

- **Minimum device**: iPhone 12+ gives modern features (5G, LiDAR)
- **Universal vs iPhone-only**: iPad support increases reach but requires adaptive UI
- **Apple Silicon Macs**: Mac Catalyst or SwiftUI multiplatform extends reach

---

## Localization & Markets

### Priority Markets by App Store Revenue
1. United States
2. China (requires special considerations)
3. Japan
4. United Kingdom
5. Germany

### Localization Checklist
- [ ] UI strings with proper pluralization
- [ ] Date/time/number formatting (use system formatters)
- [ ] Currency and pricing (use StoreKit for IAP)
- [ ] Right-to-left (RTL) support for Arabic/Hebrew
- [ ] Cultural considerations (colors, imagery, examples)
- [ ] Local payment methods and regulations

---

## Compliance Requirements

### Privacy

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **ATT** | User consent for cross-app tracking | Show ATT prompt; handle denial gracefully |
| **Privacy Nutrition Labels** | App Store disclosure of data collection | Audit all data collection; update on changes |
| **GDPR** | EU data rights | Consent, access, deletion, portability |
| **COPPA** | Children's privacy (if targeting <13) | Parental consent, no third-party analytics |
| **CCPA/CPRA** | California data rights | "Do Not Sell" option |

### Regional Considerations
- China: Data localization, ICP license for certain services
- Brazil: LGPD compliance
- Germany: Strict data protection enforcement

---

## Accessibility Requirements

Apple considers accessibility a core value. Apps that fail basic accessibility risk App Store rejection and exclude ~15-20% of users.

### Accessibility Tiers

**Tier 1: Required (Non-negotiable)**
- [ ] VoiceOver labels for all interactive elements
- [ ] VoiceOver hints for complex controls
- [ ] 44x44pt minimum tap targets
- [ ] Dynamic Type support (text scales 50% - 310%)
- [ ] Color independence (no color-only information)
- [ ] Logical reading order
- [ ] Focus management after state changes
- [ ] Error announcements

**Tier 2: Expected**
- [ ] Reduce Motion alternatives
- [ ] Bold Text support
- [ ] Increase Contrast support
- [ ] Custom VoiceOver actions
- [ ] Accessibility value for dynamic content

**Tier 3: Excellence**
- [ ] Per-app text size settings
- [ ] Audio descriptions for video
- [ ] Full keyboard navigation (iPadOS/macOS)
- [ ] Haptic feedback

### Testing Checklist
1. VoiceOver walkthrough (entire feature, eyes closed)
2. Dynamic Type at largest accessibility size
3. Bold Text enabled
4. Reduce Motion enabled
5. Increase Contrast enabled
6. Smart Invert Colors
7. Keyboard navigation (iPadOS)

### App Store Rejection Risks
- Missing VoiceOver labels on critical UI
- Tap targets below 44x44 points
- Text that doesn't scale with Dynamic Type
- Color-only information
- Inaccessible onboarding blocking app usage

---

## Analytics Implementation

### Event Naming Convention
- User actions: `action_verb_noun` (e.g., `tapped_share_button`)
- Screen views: `viewed_screen_name` (e.g., `viewed_recipe_detail`)
- Conversions: `completed_flow_name` (e.g., `completed_onboarding`)
- State changes: `changed_state_property` (e.g., `enabled_notifications`)

### Apple Privacy Compliance
- [ ] No cross-app tracking without ATT consent
- [ ] No IDFA usage without ATT prompt
- [ ] Privacy Nutrition Labels updated
- [ ] User opt-out respected
- [ ] No PII in event properties without consent

### Useful Native Signals

```swift
// Accessibility state (for segmented analytics)
UIAccessibility.isVoiceOverRunning
UIApplication.shared.preferredContentSizeCategory.isAccessibilityCategory
UIAccessibility.isReduceMotionEnabled

// App Store analytics baseline
// Use App Store Connect for installs, sessions, retention
```

### Recommended Tracking
- Accessibility tech usage (% of sessions with VoiceOver, larger text, etc.)
- Task completion by accessibility state
- Accessibility-specific error rates

---

## Resources

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Accessibility](https://developer.apple.com/accessibility/)
- [WWDC Videos](https://developer.apple.com/videos/)
