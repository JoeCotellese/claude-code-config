# ABOUTME: RICE prioritization framework reference for product managers.
# ABOUTME: Includes formula, scoring scales, examples, and facilitation tips.

# RICE Scoring Framework

## Overview

RICE is a prioritization framework developed by Intercom that scores initiatives based on four factors:
- **R**each: How many users will this affect?
- **I**mpact: How much will it affect each user?
- **C**onfidence: How certain are we about our estimates?
- **E**ffort: How much work will this take?

## The Formula

```
RICE Score = (Reach × Impact × Confidence) / Effort
```

Higher scores indicate higher priority.

---

## Scoring Scales

### Reach
*How many users will be affected per quarter?*

| Score | Description | Example |
|-------|-------------|---------|
| 10,000+ | Affects all users | Core feature improvement |
| 5,000 | Affects most users | Dashboard redesign |
| 1,000 | Affects many users | Export functionality |
| 500 | Affects some users | Admin-only feature |
| 100 | Affects few users | Enterprise-only feature |

**Tip**: Use actual data when possible (DAU, feature usage analytics). For new features, estimate based on similar existing features.

### Impact
*How much will this move the needle for each affected user?*

| Score | Impact Level | Description |
|-------|--------------|-------------|
| 3 | Massive | Solves a major pain point, significant behavior change |
| 2 | High | Notable improvement, users will appreciate |
| 1 | Medium | Incremental improvement, nice to have |
| 0.5 | Low | Minimal impact, barely noticeable |
| 0.25 | Minimal | Very minor improvement |

**Tip**: Be honest about impact. Most features are 1 (Medium). Reserve 3 for true game-changers.

### Confidence
*How confident are we in our Reach and Impact estimates?*

| Score | Confidence Level | Evidence |
|-------|------------------|----------|
| 100% | High | Data-backed, validated with users, similar past features |
| 80% | Medium | Some data, reasonable assumptions, feedback from users |
| 50% | Low | Gut feel, no direct evidence, speculative |

**Tip**: Low confidence should trigger research, not rejection. Use 50% to flag items needing validation.

### Effort
*Person-months of work required*

| Score | Effort Level | Typical Work |
|-------|--------------|--------------|
| 0.5 | Tiny | A few hours, single engineer |
| 1 | Small | 1-2 weeks, one engineer |
| 2 | Medium | 2-4 weeks, one engineer or team |
| 3 | Large | 1-2 months, team effort |
| 5+ | Huge | Quarter+ of work, multiple teams |

**Tip**: Include design, QA, documentation, and deployment time. Underestimating effort is the most common mistake.

---

## Example Scoring Session

### Feature: In-App Notifications

| Factor | Score | Reasoning |
|--------|-------|-----------|
| Reach | 8,000 | 80% of MAU uses the web app daily |
| Impact | 2 | Reduces missed updates, improves engagement |
| Confidence | 80% | Based on user feedback surveys, competitor analysis |
| Effort | 2 | Requires backend, frontend, preferences UI |

**RICE Score** = (8,000 × 2 × 0.8) / 2 = **6,400**

### Feature: Dark Mode

| Factor | Score | Reasoning |
|--------|-------|-----------|
| Reach | 10,000 | All users benefit |
| Impact | 0.5 | Nice to have, not solving a real problem |
| Confidence | 100% | Standard feature, well-understood |
| Effort | 1 | Primarily CSS, some preference logic |

**RICE Score** = (10,000 × 0.5 × 1.0) / 1 = **5,000**

### Feature: API Rate Limit Dashboard

| Factor | Score | Reasoning |
|--------|-------|-----------|
| Reach | 500 | Only API-heavy enterprise customers |
| Impact | 3 | Prevents production incidents, major pain point |
| Confidence | 80% | Multiple enterprise escalations about this |
| Effort | 1.5 | New dashboard page, backend metrics |

**RICE Score** = (500 × 3 × 0.8) / 1.5 = **800**

---

## When to Use RICE

**Good for:**
- Comparing features of different sizes and types
- Defending prioritization decisions with data
- Reducing emotional/political influence on roadmaps
- Teams that need a structured approach

**Not ideal for:**
- Very early-stage products (not enough data)
- Highly technical infrastructure work (hard to measure Reach)
- Strategic bets where Impact is intentionally speculative

---

## Common Mistakes

### 1. Inflating Impact
Everyone thinks their feature is high-impact. Calibrate by asking: "Compared to [known high-impact feature], how does this compare?"

### 2. Underestimating Effort
Include design, QA, edge cases, documentation, ops. Add 20-50% buffer for unknowns.

### 3. Ignoring Confidence
A speculative high score isn't better than a confident medium score. Use Confidence to drive research prioritization.

### 4. Comparing Incomparables
RICE works best within a category (e.g., all user-facing features). Don't compare infrastructure refactors to user features.

---

## Facilitation Tips

When running a RICE session with stakeholders:

1. **Pre-populate what you know** - Fill in Reach from analytics, Effort from engineering estimates
2. **Debate Impact and Confidence** - These are the subjective factors worth discussing
3. **Timebox discussions** - 5-10 minutes per feature max
4. **Document reasoning** - Scores without context are useless later
5. **Re-score periodically** - Confidence increases as you learn more

---

## Alternatives to RICE

- **ICE** (Impact, Confidence, Ease): Simpler, drops Reach
- **Value/Effort Matrix**: Visual 2x2, less granular
- **Weighted Scoring**: Custom criteria beyond RICE's four
- **WSJF** (Weighted Shortest Job First): SAFe framework, includes cost of delay

See other framework references for these alternatives.
