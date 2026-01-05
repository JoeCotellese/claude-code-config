# PostHog Patterns

Patterns for building insights and dashboards via PostHog MCP.

## Available MCP Tools

### Discovery
- `posthog__event-definitions-list` - List all events in project
- `posthog__properties-list` - List all properties
- `posthog__projects-get` - List available projects
- `posthog__switch-project` - Switch active project

### Insights
- `posthog__insight-create-from-query` - Create insight from HogQL/query
- `posthog__insight-query` - Run ad-hoc query
- `posthog__insights-get-all` - List all insights
- `posthog__insight-get` - Get specific insight
- `posthog__insight-update` - Modify insight
- `posthog__insight-delete` - Remove insight

### Dashboards
- `posthog__dashboard-create` - Create dashboard
- `posthog__dashboards-get-all` - List dashboards
- `posthog__dashboard-get` - Get dashboard details
- `posthog__dashboard-update` - Modify dashboard
- `posthog__add-insight-to-dashboard` - Add insight to dashboard
- `posthog__dashboard-delete` - Remove dashboard

### Queries
- `posthog__query-run` - Execute HogQL query
- `posthog__query-generate-hogql-from-question` - Generate HogQL from natural language

## Insight Types

### Trends
Track event counts over time.

**Use for:**
- Daily/weekly active users
- Feature usage over time
- Event volume monitoring

**Query pattern:**
```
SELECT count() FROM events
WHERE event = 'feature_used'
GROUP BY toStartOfDay(timestamp)
```

### Funnels
Track conversion through steps.

**Use for:**
- Onboarding completion
- Checkout flow
- Feature adoption paths

**Key settings:**
- Conversion window (e.g., 7 days)
- Breakdown by property (segment analysis)
- Exclusion steps (what shouldn't happen between)

### Retention
Track users returning over time.

**Use for:**
- Week-over-week retention
- Feature stickiness
- Cohort analysis

**Cohort types:**
- First time: Based on first event occurrence
- Recurring: Based on repeated event

### Paths
Visualize user navigation flows.

**Use for:**
- Understanding user journeys
- Finding unexpected patterns
- Identifying drop-off points

### Lifecycle
Segment users by activity status.

**Categories:**
- New: First time performing event
- Returning: Did event, then did again
- Resurrecting: Stopped, then came back
- Dormant: Did event, then stopped

## Common Insight Patterns

### Daily Active Users (DAU)
```
Event: session_started (or any core action)
Type: Trend
Display: Line chart
Interval: Day
```

### Feature Adoption Rate
```
Events: [feature_first_used]
Type: Trend
Display: Cumulative line
Math: Unique users
Compare: Previous period
```

### Onboarding Funnel
```
Steps:
1. onboarding_started
2. onboarding_step_1_completed
3. onboarding_step_2_completed
4. onboarding_completed

Type: Funnel
Window: 7 days
Breakdown: acquisition_source (optional)
```

### Feature Usage Breakdown
```
Event: feature_used
Type: Trend
Breakdown: feature_name
Display: Bar chart / Table
Math: Total count or Unique users
```

### Error Rate
```
Events:
- Numerator: error_occurred
- Denominator: session_started

Type: Trend (Formula: A/B)
Display: Line chart
Alert: > 5%
```

### Conversion Funnel
```
Steps:
1. trial_started
2. paywall_viewed
3. subscription_started

Type: Funnel
Window: 30 days
Breakdown: subscription_tier
```

### Weekly Retention
```
First event: user_signed_up
Return event: session_started
Type: Retention
Period: Week
Display: Retention table
```

## Dashboard Patterns

### Executive Dashboard
High-level business health:
- DAU/WAU/MAU trend
- New user signups
- Conversion rate
- Revenue metrics (if tracked)
- Key funnel completion rates

### Onboarding Dashboard
New user experience:
- Onboarding funnel
- Step completion rates
- Time to complete
- Drop-off points
- Onboarding by cohort

### Feature Dashboard
Per-feature deep dive:
- Usage trend
- Unique users
- Session distribution
- Feature-specific funnel
- User segments

### Error Dashboard
Technical health:
- Error rate over time
- Errors by type
- Errors by screen
- Error impact (users affected)
- Recent error samples

## Dashboard Organization

### Naming Convention
```
[Area] - [Focus]

Examples:
- Core - Daily Health
- Onboarding - Funnel Analysis
- Feature - Timer Usage
- Growth - Acquisition Sources
```

### Layout Guidelines
1. **Top row**: Key metrics (DAU, conversion rate, error rate)
2. **Middle**: Primary funnels and trends
3. **Bottom**: Breakdowns and detailed analysis

### Refresh Cadence
- Real-time: Error dashboards
- Hourly: Active user counts
- Daily: Funnels, retention
- Weekly: Cohort analysis

## HogQL Quick Reference

### Basic Queries
```sql
-- Event count
SELECT count() FROM events WHERE event = 'button_tapped'

-- Unique users
SELECT count(DISTINCT distinct_id) FROM events WHERE event = 'feature_used'

-- With time grouping
SELECT toStartOfDay(timestamp) as day, count()
FROM events
WHERE event = 'session_started'
GROUP BY day
ORDER BY day

-- Property filter
SELECT count() FROM events
WHERE event = 'feature_used'
AND properties.feature_name = 'timer'

-- Multiple events
SELECT event, count() FROM events
WHERE event IN ('onboarding_started', 'onboarding_completed')
GROUP BY event
```

### Funnel Query
```sql
SELECT
  countIf(event = 'checkout_started') as step1,
  countIf(event = 'checkout_completed') as step2,
  step2 / step1 as conversion_rate
FROM events
WHERE timestamp > now() - INTERVAL 7 DAY
```

### Property Breakdown
```sql
SELECT
  properties.screen_name as screen,
  count() as views
FROM events
WHERE event = 'screen_viewed'
GROUP BY screen
ORDER BY views DESC
LIMIT 10
```

## Workflow: Question to Dashboard

1. **Start with PM question** (from discovery)
2. **Check existing events** (`event-definitions-list`)
3. **Identify or create needed events**
4. **Create insight** (`insight-create-from-query`)
5. **Verify data** (`insight-query` or view in UI)
6. **Create/update dashboard** (`dashboard-create`)
7. **Add insight to dashboard** (`add-insight-to-dashboard`)
8. **Document** what question each insight answers
