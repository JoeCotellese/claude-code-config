
# Analytics Framework
This reference provides a platform-agnostic approach to analytics implementation for product features.

---

## Analytics Event Types

For every feature, define events across these categories:

### User Actions
Track user-initiated interactions.

**Naming pattern**: `object_action`, past tense (matches product-analytics `references/event-taxonomy.md`)

| Example | Trigger |
|---------|---------|
| `share_button_tapped` | User taps share icon |
| `signup_button_clicked` | User clicks signup CTA |
| `search_query_submitted` | User submits search |
| `recipe_card_swiped` | User swipes to dismiss |

### Screen/Page Views
Track navigation and content consumption.

**Naming pattern**: `screen_name_viewed`

| Example | Trigger |
|---------|---------|
| `recipe_detail_viewed` | Recipe detail page loads |
| `settings_viewed` | Settings screen opens |
| `search_results_viewed` | Search results displayed |

### Conversions
Track completion of key user flows.

**Naming pattern**: `flow_name_completed`

| Example | Trigger |
|---------|---------|
| `onboarding_completed` | User finishes onboarding flow |
| `purchase_completed` | Purchase transaction succeeds |
| `signup_completed` | Account creation succeeds |

### State Changes
Track important system or user state transitions.

**Naming pattern**: `state_property_changed` or `feature_enabled/disabled`

| Example | Trigger |
|---------|---------|
| `notifications_enabled` | User turns on notifications |
| `user_logged_out` | User signs out |
| `plan_upgraded` | User upgrades subscription tier |

---

## Event Properties

Every event should include relevant context:

### Standard Properties (Always Include)
- `timestamp` - When the event occurred
- `user_id` - Anonymized user identifier (if logged in)
- `session_id` - Current session identifier
- `platform` - iOS/Android/Web
- `app_version` - Application version

### Feature-Specific Properties
Add context relevant to the event:

```
event: share_button_tapped
properties:
  content_id: "recipe_123"
  content_type: "recipe"
  share_method: "native_share_sheet"
  source_screen: "recipe_detail"
```

### Property Guidelines
- Use snake_case for consistency
- Use enums over free text when possible
- Avoid PII (names, emails, exact locations)
- Include enough context to answer "why?"

---

## Success Metrics by Feature Type

### Engagement Features
*Goal: Increase user activity*

| Metric | Description | Target Example |
|--------|-------------|----------------|
| **DAU/MAU** | Daily/Monthly Active Users | 10% increase |
| **Session Duration** | Average time per session | +15% |
| **Session Frequency** | Sessions per user per week | +20% |
| **Feature Usage Rate** | % of users who use feature | >30% of active users |

### Retention Features
*Goal: Keep users coming back*

| Metric | Description | Target Example |
|--------|-------------|----------------|
| **D1/D7/D30 Retention** | % returning after N days | D7 > 40% |
| **Churn Rate** | % of users who stop using | <5% monthly |
| **Resurrection Rate** | % of lapsed users returning | +10% |
| **Cohort Retention** | Retention curves by signup cohort | Flatter curve |

### Monetization Features
*Goal: Increase revenue*

| Metric | Description | Target Example |
|--------|-------------|----------------|
| **Conversion Rate** | % who complete purchase | >3% |
| **ARPU** | Average Revenue Per User | +$0.50 |
| **LTV** | Lifetime Value per user | +15% |
| **Paywall View → Purchase** | Funnel conversion | >10% |

### Content Features
*Goal: Increase content consumption*

| Metric | Description | Target Example |
|--------|-------------|----------------|
| **Content View Rate** | Views per user per session | +25% |
| **Completion Rate** | % who finish content | >60% |
| **Save/Bookmark Rate** | % who save for later | >10% |
| **Content Diversity** | Unique content types consumed | +2 types |

### Social Features
*Goal: Drive viral growth*

| Metric | Description | Target Example |
|--------|-------------|----------------|
| **Invite Sent Rate** | % of users who invite | >20% |
| **Invite Acceptance Rate** | % of invites that convert | >30% |
| **K-Factor** | Viral coefficient | >0.5 |
| **Share Rate** | % of content shared externally | >5% |

---

## A/B Testing Framework

When running experiments, define:

### 1. Hypothesis
What you believe will happen and why.

> "Adding social proof (user count) to the paywall will increase conversion because it reduces uncertainty."

### 2. Variants
- **Control (A)**: Current experience
- **Treatment (B)**: New experience with change

Keep variants minimal—test one variable at a time.

### 3. Primary Metric
The ONE metric that determines success.

- Must be directly influenced by the change
- Must be measurable within test duration
- Must be important to the business

### 4. Secondary Metrics
Supporting metrics to monitor for unintended effects:
- Guardrail metrics (shouldn't get worse)
- Diagnostic metrics (help explain results)

### 5. Sample Size
Users needed per variant for statistical significance.

Factors:
- Baseline conversion rate
- Minimum detectable effect (MDE)
- Statistical significance level (usually 95%)
- Statistical power (usually 80%)

Use a [sample size calculator](https://www.evanmiller.org/ab-testing/sample-size.html).

### 6. Duration
Minimum test runtime:
- At least 1-2 full weeks (capture weekly patterns)
- Long enough to reach sample size
- Consider novelty effects (initial spike, then normalize)

### 7. Success Criteria
Define before the test starts:
- What effect size is meaningful? (e.g., +5% conversion)
- What confidence level is required? (e.g., 95%)
- What happens if results are inconclusive?

---

## Dashboard Requirements

For each feature, specify monitoring needs:

### Real-Time Monitoring
Events that need immediate visibility (within minutes):
- Critical errors
- Payment failures
- Security events
- Launch-day feature usage

### Daily Reports
Aggregate metrics reviewed daily:
- Feature adoption rates
- Conversion funnels
- Error rates
- Key engagement metrics

### Weekly Reviews
Trend analysis and deeper dives:
- Cohort comparisons
- Retention curves
- Experiment results
- Revenue analysis

### Alerts
Automatic notifications when thresholds are crossed:

| Alert Type | Trigger | Response |
|------------|---------|----------|
| Error spike | Error rate > 5% | Investigate immediately |
| Conversion drop | Daily conversion < 80% baseline | Review changes, possible rollback |
| Performance degradation | P95 latency > 2s | Investigate infrastructure |

---

## Data Quality Checklist

Before launching analytics:

### Implementation
- [ ] Events fire at correct moments
- [ ] All required properties included
- [ ] Property values are correct types
- [ ] Events appear in analytics dashboard
- [ ] No duplicate events

### Validation
- [ ] Test on multiple devices/browsers
- [ ] Test with slow network
- [ ] Test error scenarios
- [ ] Verify user_id consistency
- [ ] Check timestamp accuracy

### Documentation
- [ ] Event schema documented
- [ ] Business context explained
- [ ] Dashboard location noted
- [ ] Alert owners assigned

---

## Privacy Considerations

### General Principles
- Collect minimum necessary data
- Anonymize where possible
- Provide opt-out mechanism
- Document data collection in privacy policy

### Platform-Specific
For Apple-specific privacy requirements, see `platforms/apple.md`.
For web-specific privacy requirements, see `platforms/web.md`.

### Common Pitfalls
- Accidentally logging PII in properties
- Not respecting user opt-out preferences
- Retaining data longer than necessary
- Sharing data with third parties without consent

---

## Analytics Tool Comparison

| Tool | Best For | Considerations |
|------|----------|----------------|
| **Amplitude** | Product analytics, cohorts | More expensive at scale |
| **Mixpanel** | Event analytics, funnels | Similar to Amplitude |
| **PostHog** | Self-hosted, privacy-focused | Open source option |
| **Google Analytics** | Web traffic, marketing | Less suited for product analytics |
| **Segment** | Data routing to multiple tools | Adds cost but flexibility |

### Tool Selection Criteria
- Scale (events/month)
- Privacy requirements
- Budget
- Team expertise
- Integration needs
