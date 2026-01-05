# Event Taxonomy Guide

## Naming Convention: `noun_verb`

Format: `{entity}_{action}` or `{entity}_{action}_{detail}`

### Why noun_verb?
- Alphabetical grouping by entity in PostHog
- Easy filtering (`user_*`, `checkout_*`)
- Consistent mental model across team

### Standard Entities

| Entity | Description | Examples |
|--------|-------------|----------|
| `user` | Account/auth actions | `user_signed_up`, `user_logged_in` |
| `session` | App session lifecycle | `session_started`, `session_ended` |
| `screen` | Screen/page views | `screen_viewed` with `screen_name` property |
| `button` | Tappable UI elements | `button_tapped` with `button_id` property |
| `feature` | Feature interactions | `feature_used` with `feature_name` property |
| `error` | Error occurrences | `error_occurred` with `error_type` property |
| `payment` | Transaction events | `payment_initiated`, `payment_completed` |
| `subscription` | Subscription lifecycle | `subscription_started`, `subscription_cancelled` |
| `onboarding` | Onboarding flow | `onboarding_started`, `onboarding_step_completed` |
| `search` | Search interactions | `search_performed`, `search_result_selected` |
| `share` | Sharing actions | `share_initiated`, `share_completed` |
| `notification` | Push/local notifications | `notification_received`, `notification_opened` |

### Standard Actions

| Action | When to use |
|--------|-------------|
| `viewed` | User sees something |
| `tapped` / `clicked` | User interacts with element |
| `started` | Beginning of process |
| `completed` | Successful end of process |
| `failed` | Unsuccessful end of process |
| `cancelled` | User-initiated cancellation |
| `skipped` | User bypassed optional step |
| `selected` | User chose from options |
| `submitted` | Form/data submission |
| `updated` | Data modification |
| `deleted` | Data removal |
| `enabled` / `disabled` | Toggle states |

### Required Properties

Every event MUST include:
```
timestamp        // Auto-captured by PostHog
distinct_id      // User identifier
$screen_name     // Current screen (mobile)
$current_url     // Current page (web)
```

### Property Naming

Use `snake_case` for all properties:
```
button_id: "submit_form"
screen_name: "checkout"
error_type: "network_timeout"
duration_ms: 1234
item_count: 3
```

### Event Categories

Group events by product area for dashboards:

| Category | Prefix Pattern | Dashboard |
|----------|---------------|-----------|
| Authentication | `user_*` | Auth Funnel |
| Onboarding | `onboarding_*` | Onboarding Funnel |
| Core Feature | `{feature}_*` | Feature Usage |
| Monetization | `payment_*`, `subscription_*` | Revenue |
| Engagement | `session_*`, `screen_*` | Engagement |
| Errors | `error_*` | Error Monitoring |

### Funnel Events Pattern

For any multi-step flow, define clear step events:

```
{flow}_started
{flow}_step_{n}_completed  // or {flow}_{step_name}_completed
{flow}_completed
{flow}_abandoned
```

Example - Checkout:
```
checkout_started
checkout_address_entered
checkout_payment_entered
checkout_completed
checkout_abandoned
```

### Analyze Existing Patterns First

Before adding new events, always:
1. Search codebase for existing analytics calls
2. Document current naming patterns
3. Adopt existing conventions for consistency
4. Only introduce new patterns if none exist
