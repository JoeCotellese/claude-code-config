# Apple Platform Considerations

This reference provides Apple-specific platform capabilities, constraints, and business considerations for product planning.

## Platform Capabilities to Consider

### iOS/iPadOS Specific
- **Widgets**: Home Screen, Lock Screen, StandBy mode
- **Live Activities**: Real-time updates on Lock Screen and Dynamic Island
- **App Clips**: Lightweight app experiences without full installation
- **Shortcuts**: Siri Shortcuts and automation support
- **Focus Filters**: App-specific Focus mode behavior
- **Handoff**: Continuity between devices

### Apple Ecosystem Integration
- **iCloud**: CloudKit for data sync, iCloud Drive for documents
- **Sign in with Apple**: Privacy-focused authentication (required if offering third-party auth)
- **SharePlay**: Synchronized experiences during FaceTime
- **AirDrop**: Peer-to-peer content sharing
- **Universal Clipboard**: Copy/paste between devices

### Device-Specific Features
- **iPhone**: Dynamic Island (14 Pro+), Action Button (15 Pro+), Camera Control (16+)
- **iPad**: Split View, Slide Over, Stage Manager, Apple Pencil, trackpad/keyboard support
- **Apple Watch**: Always-on display, complications, Digital Crown, background modes
- **Apple TV**: Siri Remote, multi-user support, Picture in Picture

### Privacy & Security
- **App Tracking Transparency (ATT)**: User consent for tracking
- **Privacy Nutrition Labels**: Required App Store disclosures
- **Keychain**: Secure credential storage
- **Face ID / Touch ID**: Biometric authentication
- **Secure Enclave**: Hardware-based security

## App Store Guidelines Impact

### Common Rejection Reasons
- **2.1 - App Completeness**: Crashes, bugs, placeholder content
- **4.3 - Spam**: Too similar to existing apps, repetitive content
- **5.1.1 - Privacy**: Missing privacy policy or improper data handling
- **2.3.10 - Accurate Metadata**: Misleading descriptions or screenshots
- **3.1.1 - In-App Purchase**: Using non-IAP payment for digital goods

### Business Model Constraints
- **Digital Goods**: Must use In-App Purchase (Apple's 30/15% commission)
- **Physical Goods/Services**: Can use external payment processors
- **Reader Apps**: Can link to external subscription management
- **External Links**: New rules allow limited linking out (with entitlement)

### Subscription Considerations
- **Pricing Tiers**: Apple's predefined price points
- **Introductory Offers**: Free trials, pay-up-front, pay-as-you-go
- **Family Sharing**: Automatic for most subscriptions
- **Refund Windows**: Customer refund policies affect retention metrics

## Monetization Strategy Guide

### In-App Purchase (IAP) vs Subscription

**Choose IAP when:**
- Content is consumable (coins, power-ups, etc.)
- One-time feature unlocks (remove ads, pro features)
- Content packs or expansions
- User prefers one-time purchase over recurring cost

**Choose Subscription when:**
- Ongoing service or content updates
- Regular operational costs (server, API, content creation)
- Want predictable recurring revenue
- Offering tiered access levels

**IAP Pros:**
- Lower friction (one-time decision)
- Better for users who dislike subscriptions
- Can price-discriminate with bundles

**IAP Cons:**
- Unpredictable revenue
- Lower lifetime value (LTV)
- Can't update pricing after purchase

**Subscription Pros:**
- Predictable recurring revenue
- Higher LTV per user
- Can adjust pricing over time
- Better retention metrics visibility

**Subscription Cons:**
- Higher initial friction
- User fatigue with "subscription everything"
- Requires ongoing value delivery

### Freemium vs Paid Upfront vs Trial

**Freemium:**
- Best for: Social apps, content platforms, utility apps
- Conversion rates: 2-5% typically
- Requires: Strong free experience, clear premium value

**Paid Upfront:**
- Best for: Professional tools, specialized apps, games
- Discovery challenge: Users won't try before buying
- Requires: Strong differentiation, clear screenshots

**Free Trial:**
- Best for: Subscription apps, complex products
- Common durations: 7 days, 14 days, 1 month
- Requires: Onboarding that demonstrates value quickly

## Version and Device Support

### iOS Version Strategy
- **Latest iOS**: Full feature support, shortest review times
- **iOS N-1**: Previous year's version, balance of reach vs features
- **iOS N-2**: Broader reach, limited to older APIs

**Typical support window:** Latest 2-3 major iOS versions

### Device Compatibility
- **Consider minimum device**: iPhone 12+ gives access to modern features (5G, LiDAR, better cameras)
- **Universal vs iPhone-only**: iPad support increases reach but requires adaptive UI
- **Apple Silicon Macs**: Mac Catalyst or SwiftUI multiplatform increases reach

## Localization & Markets

### Priority Markets (by App Store revenue)
1. United States
2. China (requires special considerations)
3. Japan
4. United Kingdom
5. Germany

### Localization Checklist
- UI strings with proper pluralization
- Date/time/number formatting
- Currency and pricing
- Right-to-left (RTL) language support for Arabic/Hebrew
- Cultural considerations (colors, imagery, examples)
- Local payment methods and regulations

## Compliance Requirements

### COPPA (Children's Privacy)
- If targeting users under 13, strict requirements apply
- "Kids" category has additional restrictions
- Cannot include third-party advertising or analytics without parental consent

### GDPR (Europe)
- User consent for data collection
- Right to access, correct, delete data
- Data portability requirements

### Regional Laws
- California CCPA/CPRA
- Brazil LGPD
- China data localization requirements
