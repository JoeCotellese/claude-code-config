# Analytics Framework

This reference provides the standard analytics implementation approach for Apple platform features.

## Analytics Events to Track

For every feature or requirement, specify:

### User Actions
- Button taps, gesture interactions, menu selections
- Named using `action_verb_noun` pattern (e.g., `tapped_share_button`, `swiped_recipe_card`)

### Screen Views
- Every screen/view that appears to the user
- Named using `viewed_screen_name` pattern (e.g., `viewed_recipe_detail`, `viewed_settings`)

### Conversions
- Completion of key user flows
- Named using `completed_flow_name` pattern (e.g., `completed_onboarding`, `completed_purchase`)

### State Changes
- Important system or user state transitions
- Named using `changed_state_property` pattern (e.g., `enabled_notifications`, `logged_out`)

## Success Metrics by Feature Type

### Engagement Features
- **Primary**: Daily Active Users (DAU), Session Duration, Session Frequency
- **Secondary**: Feature Usage Rate, Time in Feature

### Retention Features
- **Primary**: Day 1/7/30 Retention Rate, Churn Rate
- **Secondary**: Return Visit Rate, Long-term User Percentage

### Monetization Features
- **Primary**: Conversion Rate, Average Revenue Per User (ARPU)
- **Secondary**: Funnel Completion Rate, Time to Conversion

### Content Features
- **Primary**: Content View Rate, Content Completion Rate
- **Secondary**: Content Share Rate, Content Save Rate

### Social Features
- **Primary**: Invitation Sent Rate, Invitation Acceptance Rate
- **Secondary**: Social Action Rate, Network Growth

## A/B Testing Framework

When applicable, define:

1. **Hypothesis**: What you believe will happen and why
2. **Variants**: Control (A) and treatment (B) descriptions
3. **Primary Metric**: The one metric that determines success
4. **Secondary Metrics**: Supporting metrics to monitor
5. **Sample Size**: Required users per variant
6. **Duration**: Test runtime (typically 1-2 weeks minimum)
7. **Success Criteria**: Minimum effect size to declare winner

## Dashboard Requirements

For each feature, specify:

1. **Real-time Monitoring**: Events that need immediate visibility
2. **Daily Reports**: Aggregate metrics reviewed daily
3. **Weekly Reviews**: Trend analysis and cohort comparisons
4. **Alerts**: Thresholds that trigger notifications (drops, spikes, errors)

## Apple-Specific Considerations

### Privacy
- All events must comply with Apple's App Tracking Transparency (ATT)
- User consent required for cross-app tracking
- No PII in event properties without explicit consent

### App Store Requirements
- Analytics must not be used to build user profiles for advertising without consent
- Data collection must be disclosed in Privacy Nutrition Labels
- Users must be able to opt-out of analytics

### Implementation Notes
- Use Apple's native frameworks when possible (StoreKit for purchases, etc.)
- Consider App Store Connect analytics as baseline
- Tag events with app version for regression analysis
