---
name: product-analytics
description: Product analytics skill for analyzing codebases, suggesting analytics events, interviewing product managers about key questions, and building PostHog insights and dashboards. Use this skill when the user wants to (1) analyze a codebase for analytics opportunities, (2) discover what questions a PM wants to answer with data, (3) create or modify PostHog insights/dashboards, (4) add new analytics events to a codebase, or (5) understand analytics architecture patterns. Primary users are product managers and frontend developers seeking visibility into product usage. (user)
---

# Product Analytics

Enable product visibility through analytics discovery, implementation, and PostHog dashboards.

## Core Capabilities

### 1. Codebase Analysis
Analyze existing code for analytics patterns and suggest new events.

**Workflow:**
1. Search for existing analytics calls (grep for `analytics`, `track`, `capture`, `report`)
2. Document current naming conventions and patterns
3. Identify gaps: screens without tracking, features without usage metrics
4. Suggest events following existing patterns or [event-taxonomy.md](references/event-taxonomy.md)

### 2. PM Discovery
Conversational process to uncover what questions need answering.

**Flow:** Business context → Current state → Key questions → Feature deep-dives → Prioritization

See [pm-discovery.md](references/pm-discovery.md) for the full framework.

**Output:** Question-to-metric mapping ready for implementation.

### 3. PostHog Insights & Dashboards
Build analytics views using PostHog MCP tools.

**Available operations:**
- List events/properties in project
- Create insights (trends, funnels, retention)
- Build and organize dashboards
- Run HogQL queries

See [posthog-patterns.md](references/posthog-patterns.md) for insight patterns and HogQL reference.

### 4. Event Implementation
Add analytics events to codebases without deep developer involvement.

**Pattern:** Facade → Strategy → Adapter → Observer

See [analytics-architecture.md](references/analytics-architecture.md) for language-agnostic implementation patterns.

**PM-friendly workflow:**
1. Find event enum/definition file
2. Add new event case with typed properties
3. Call facade from UI code: `analytics.report(.eventName(property: value))`

## Quick Reference

| Task | Reference |
|------|-----------|
| Naming events | [event-taxonomy.md](references/event-taxonomy.md) |
| Discovering PM needs | [pm-discovery.md](references/pm-discovery.md) |
| Creating PostHog insights | [posthog-patterns.md](references/posthog-patterns.md) |
| Adding events to code | [analytics-architecture.md](references/analytics-architecture.md) |

## Workflow: End-to-End

```
1. Discovery (PM interview)
   ↓
2. Codebase Analysis (existing events)
   ↓
3. Event Planning (new events needed)
   ↓
4. Implementation (add to codebase)
   ↓
5. PostHog Setup (insights + dashboard)
   ↓
6. Validation (verify data flowing)
```

## PostHog MCP Tools

Load tools via MCPSearch before use:
- `posthog__event-definitions-list` - List events
- `posthog__insight-create-from-query` - Create insight
- `posthog__dashboard-create` - Create dashboard
- `posthog__add-insight-to-dashboard` - Add to dashboard
- `posthog__query-run` - Run HogQL query
