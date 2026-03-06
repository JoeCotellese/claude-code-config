
# Kano Model
## Overview

The Kano Model, developed by Professor Noriaki Kano in the 1980s, categorizes product features based on how they affect customer satisfaction. It reveals that not all features are equal—some delight, some satisfy, and some are simply expected.

## The Five Categories

### 1. Must-Be (Basic Needs)
**If absent, customers are very dissatisfied. If present, customers are neutral.**

- Customers expect these and don't think about them until they're missing
- Having them doesn't create satisfaction, but lacking them creates strong dissatisfaction
- Typically not mentioned in surveys because they're assumed

**Examples:**
- Mobile app: Doesn't crash
- E-commerce: Secure checkout
- SaaS: Data doesn't get lost
- Recipe app: Can view recipe instructions

### 2. One-Dimensional (Performance Needs)
**Satisfaction is proportional to fulfillment level.**

- More is better (or faster, or cheaper)
- Customers explicitly ask for these
- Direct correlation between investment and satisfaction

**Examples:**
- Mobile app: Faster load times
- E-commerce: Faster shipping
- SaaS: More storage
- Recipe app: More recipes in the database

### 3. Attractive (Delighters)
**If absent, customers don't mind. If present, customers are delighted.**

- Unexpected features that pleasantly surprise
- Customers didn't know they wanted these
- Create strong positive emotional responses
- Eventually become One-Dimensional, then Must-Be over time

**Examples:**
- Mobile app: Personalized recommendations
- E-commerce: Handwritten thank-you note
- SaaS: AI-powered insights
- Recipe app: Automatic shopping list generation

### 4. Indifferent
**Customers don't care whether present or absent.**

- No impact on satisfaction either way
- Often internal features or technical improvements
- Can still be valuable (reduces support costs, enables future features)

**Examples:**
- Code refactoring (invisible to users)
- Backend database migration
- Admin-only analytics dashboards

### 5. Reverse
**Presence actually decreases satisfaction for some customers.**

- Features some users hate
- Often complexity or "bloat"
- May satisfy one segment while alienating another

**Examples:**
- Auto-play videos
- Mandatory tutorials
- Social features in a productivity app
- Gamification elements

---

## Kano Diagram

```
                  Satisfaction
                      ↑
                      │    ╱ Attractive
                      │  ╱    (Delighters)
                      │╱
    ──────────────────┼──────────────────→ Fulfillment
                     ╱│
          One-     ╱  │
       Dimensional    │
                      │
        Must-Be ──────┘
       (flat, then drops sharply)
```

- **Must-Be**: Flat until missing, then drops sharply
- **One-Dimensional**: Linear relationship
- **Attractive**: Steep increase when present, flat when absent

---

## Kano Research Method

To classify features, survey users with paired questions:

### Functional Question
"How would you feel if [feature] was present?"

### Dysfunctional Question
"How would you feel if [feature] was absent?"

### Response Options (for both)
1. I like it
2. I expect it
3. I'm neutral
4. I can tolerate it
5. I dislike it

### Classification Matrix

| Dysfunctional → | Like | Expect | Neutral | Tolerate | Dislike |
|-----------------|------|--------|---------|----------|---------|
| **Functional ↓** | | | | | |
| Like | Q | A | A | A | O |
| Expect | R | I | I | I | M |
| Neutral | R | I | I | I | M |
| Tolerate | R | I | I | I | M |
| Dislike | R | R | R | R | Q |

**Key:**
- M = Must-Be
- O = One-Dimensional
- A = Attractive
- I = Indifferent
- R = Reverse
- Q = Questionable (respondent may have misunderstood)

---

## Using Kano for Prioritization

### Step 1: Survey Your Users
- Select 15-20 potential features
- Survey representative sample (50-100+ responses)
- Classify each feature based on majority response

### Step 2: Create a Prioritization Matrix

| Priority | Category | Strategy |
|----------|----------|----------|
| 1st | Must-Be (missing) | Fix immediately - these are table stakes |
| 2nd | One-Dimensional | Invest proportionally to competitive landscape |
| 3rd | Attractive | Select 1-2 to differentiate |
| 4th | Indifferent | Deprioritize or cut |
| Avoid | Reverse | Don't build, or make optional |

### Step 3: Watch for Drift
Features migrate over time:
- **Attractive → One-Dimensional → Must-Be**
- Example: Smartphone maps were delighters in 2007, expected by 2015, basic by 2020

---

## Example: Recipe App Feature Classification

| Feature | Classification | Reasoning |
|---------|---------------|-----------|
| View recipe instructions | Must-Be | Core functionality, expected |
| Save favorite recipes | One-Dimensional | More saved = more value |
| Auto-generate shopping list | Attractive | Unexpected convenience |
| Social sharing | Indifferent | Most users don't care |
| Mandatory video tutorials | Reverse | Annoys experienced users |

---

## When to Use Kano

**Good for:**
- Understanding what customers truly value (not just what they say)
- Deciding where to invest for differentiation vs. parity
- Identifying features to cut (Indifferent, Reverse)
- Training teams to think beyond "customers asked for X"

**Not ideal for:**
- Detailed prioritization (use RICE or Weighted Scoring for that)
- B2B with few customers (need statistical significance)
- Fast-moving markets where categories shift quickly

---

## Facilitation Tips

When running Kano research:

1. **Keep surveys short** - 15-20 features max, or you'll get survey fatigue
2. **Phrase questions carefully** - "If [feature] existed..." not "Would you want..."
3. **Segment results** - Different user types may classify differently
4. **Combine with interviews** - Surveys classify, interviews explain why
5. **Re-run annually** - Categories drift as expectations change

---

## Common Mistakes

### 1. Assuming Attractive Stays Attractive
Delighters become expectations. Today's "wow" is tomorrow's "meh."

### 2. Ignoring Must-Bes
Because they don't create satisfaction, teams skip them. But one missing Must-Be can tank your product.

### 3. Over-indexing on Attractive
Delighters are expensive and become commoditized. Balance with One-Dimensional improvements.

### 4. Building Reverse Features for Loud Minorities
A few vocal users request features most users hate. Segment your research.
