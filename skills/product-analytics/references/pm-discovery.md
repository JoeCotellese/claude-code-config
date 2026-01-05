# PM Discovery Framework

Conversational framework for uncovering analytics requirements.

## Discovery Goals

1. Identify the key questions the PM wants to answer
2. Map questions to measurable events and metrics
3. Prioritize what to track first
4. Define success criteria for features

## Conversation Flow

### Phase 1: Business Context

Start by understanding the product and business goals:

**Opening questions:**
- "What's the core value proposition of this product?"
- "Who are your primary user segments?"
- "What does success look like for this product this quarter?"

**Follow-up based on responses:**
- "How would you know if users are getting that value?"
- "What behavior indicates a user 'gets it'?"

### Phase 2: Current State

Understand what visibility exists today:

- "What analytics do you have in place currently?"
- "What questions can you answer today vs. what's a black box?"
- "When you look at current data, what frustrates you most?"
- "What decisions are you making based on gut feel that you wish you had data for?"

### Phase 3: Key Questions

Dig into the specific questions they want answered:

**Prompt with categories:**

| Category | Example Questions |
|----------|------------------|
| Acquisition | "Where do users come from? Which channels convert best?" |
| Activation | "Are users completing onboarding? Where do they drop off?" |
| Engagement | "How often do users return? What features do they use?" |
| Retention | "Are users coming back? When do they churn?" |
| Revenue | "What drives conversions? What's the path to purchase?" |

**For each question they raise:**
1. "What would you do differently if you had that answer?"
2. "What's your hypothesis for what the data will show?"
3. "How frequently do you need to check this?"

### Phase 4: Feature Deep-Dives

For key features, understand the journey:

- "Walk me through the ideal user flow for [feature]"
- "What are the critical decision points?"
- "Where do you suspect users get stuck?"
- "What would 'success' look like for a user using this feature?"

**Map to funnel:**
```
Entry Point → Step 1 → Step 2 → ... → Success
         ↓         ↓         ↓
      Drop-off  Drop-off  Drop-off
```

### Phase 5: Prioritization

Not everything can be tracked at once:

- "If you could only answer ONE question, which would it be?"
- "What's the most urgent decision waiting on data?"
- "Which feature is most critical to understand right now?"

**Priority matrix:**
```
                    High Impact
                         │
         Quick Wins      │     Strategic
         (Do First)      │     (Plan For)
    ─────────────────────┼─────────────────────
         Low Priority    │     Time Sinks
         (Maybe Later)   │     (Avoid)
                         │
                    Low Impact
```

## Question-to-Metric Mapping

### Common PM Questions → Metrics

| PM Question | Event(s) Needed | Metric/Insight |
|-------------|-----------------|----------------|
| "Are users completing onboarding?" | `onboarding_started`, `onboarding_completed` | Completion rate funnel |
| "What features do users use most?" | `feature_used` with `feature_name` | Feature usage breakdown |
| "Where do users drop off in checkout?" | `checkout_*` step events | Checkout funnel |
| "Are users coming back?" | `session_started` | Retention cohort |
| "How long do users spend in the app?" | `session_started`, `session_ended` | Avg session duration |
| "What errors are users hitting?" | `error_occurred` | Error rate by type |
| "Is the new feature being adopted?" | `feature_used` filtered by feature | Feature adoption trend |
| "What's our conversion rate?" | `trial_started`, `subscription_started` | Conversion funnel |

### Turning Questions into Events

For each PM question:

1. **Identify the user action** that answers the question
2. **Define the event** using `noun_verb` convention
3. **List required properties** to segment/filter
4. **Specify the insight type** (trend, funnel, retention, etc.)

Example:
```
Question: "Are users finding value in the timer feature?"

User Action: User starts and completes a timer session
Events:
  - timer_started (duration_selected: Int)
  - timer_completed (actual_duration: Int, was_interrupted: Bool)
  - timer_cancelled (elapsed_before_cancel: Int)

Properties:
  - duration_selected: How long they intended
  - actual_duration: How long they actually used it
  - was_interrupted: Did they leave the app?

Insights:
  - Completion rate: timer_started → timer_completed funnel
  - Usage trend: timer_started count over time
  - Session length: avg(actual_duration) where completed
```

## Discovery Output Template

After discovery, summarize:

```markdown
## Analytics Discovery Summary

### Business Context
[1-2 sentences on product and goals]

### Key Questions (Priority Order)
1. [Question] → [Proposed metric/insight]
2. [Question] → [Proposed metric/insight]
3. ...

### Proposed Events
| Event | Properties | Answers Question |
|-------|------------|------------------|
| ... | ... | ... |

### Proposed Dashboards
1. [Dashboard name] - [What it shows]
2. ...

### Next Steps
1. [ ] Implement events in codebase
2. [ ] Create PostHog insights
3. [ ] Build dashboard
4. [ ] Set up alerts for key metrics
```

## Red Flags to Surface

During discovery, watch for:

- **Vanity metrics**: "We want to track page views" → Dig deeper: "What decision would that inform?"
- **Too much at once**: Start with 5-10 key events, not 50
- **No hypothesis**: If they can't guess what data will show, the question may not be actionable
- **Lagging indicators only**: Balance with leading indicators they can act on
