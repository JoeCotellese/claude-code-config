# ABOUTME: Value/Effort Matrix (2x2) prioritization framework reference.
# ABOUTME: Includes quadrant definitions, workshop format, and common pitfalls.

# Value/Effort Matrix

## Overview

The Value/Effort Matrix (also called Impact/Effort, Value/Complexity, or Priority Matrix) is a simple 2x2 grid for prioritizing features based on two dimensions:
- **Value**: Benefit to users and/or business
- **Effort**: Resources required to implement

## The Four Quadrants

```
                    High Value
                        ↑
         ┌──────────────┼──────────────┐
         │              │              │
         │   BIG BETS   │  QUICK WINS  │
         │   (Do next)  │  (Do first)  │
         │              │              │
High ────┼──────────────┼──────────────┼──── Low
Effort   │              │              │    Effort
         │  MONEY PITS  │   FILL-INS   │
         │   (Avoid)    │  (Do later)  │
         │              │              │
         └──────────────┼──────────────┘
                        ↓
                    Low Value
```

### 1. Quick Wins (High Value, Low Effort)
**Do these first.**

- Maximum ROI
- Build momentum and team morale
- Often incremental improvements

**Examples:**
- Fix high-friction UX bug
- Add commonly requested small feature
- Improve error messages

### 2. Big Bets (High Value, High Effort)
**Do these next, with planning.**

- Strategic investments
- Require careful scoping and phasing
- Break into smaller deliverables when possible

**Examples:**
- Major new product capability
- Platform rewrite for scalability
- Entering new market segment

### 3. Fill-Ins (Low Value, Low Effort)
**Do these opportunistically.**

- Nice polish items
- Good for hackathons or spare cycles
- Don't let these crowd out higher-priority work

**Examples:**
- Minor UI tweaks
- Quality-of-life improvements
- Low-traffic page redesigns

### 4. Money Pits (Low Value, High Effort)
**Avoid these.**

- Poor ROI
- Often pet projects or over-engineered solutions
- Challenge assumptions if frequently proposed

**Examples:**
- Features for edge cases affecting <1% of users
- "Gold plating" that doesn't move metrics
- Technical purity projects with no user benefit

---

## Running a Value/Effort Workshop

### Preparation

1. **Gather features** - Collect 15-30 items to prioritize
2. **Prepare the board** - Whiteboard, Miro, or FigJam with 2x2 grid
3. **Invite stakeholders** - Engineering, design, product, and relevant business leads
4. **Set expectations** - This is a sorting exercise, not a final decision

### Workshop Format (60-90 minutes)

**1. Calibration (10 min)**
- Define value criteria (user impact? revenue? strategic fit?)
- Define effort (person-weeks? complexity? risk?)
- Place 2-3 known items to anchor the scale

**2. Individual Placement (15 min)**
- Each participant silently places sticky notes
- Use different colors per participant

**3. Group Discussion (30-45 min)**
- Review items with disagreement (different quadrants)
- Discuss reasoning, converge on placement
- Timebox: 2-3 minutes per item max

**4. Prioritize Within Quadrants (10 min)**
- Rank Quick Wins 1, 2, 3...
- Rank Big Bets 1, 2, 3...
- Note: Fill-Ins and Money Pits don't need ranking

**5. Document Decisions (5 min)**
- Capture placements and key reasoning
- Identify items needing research before placement

---

## Estimating Value

Value should include multiple dimensions:

### User Value
- Pain point severity (1-5 scale)
- Frequency of problem (daily/weekly/monthly/rarely)
- Number of users affected

### Business Value
- Revenue impact (direct or indirect)
- Cost savings (support, operations)
- Strategic alignment (opens new markets, strengthens moat)

### Proxy Metrics
If hard to quantify, use:
- Customer request frequency
- NPS/CSAT correlation
- Competitive parity requirement

---

## Estimating Effort

Consider all aspects of delivery:

### Development Complexity
- New tech vs. existing patterns
- Integration requirements
- Unknown unknowns (spikes needed?)

### Scope
- Number of screens/features
- Data model changes
- API surface area

### Dependencies
- Other teams involved
- External vendors
- Regulatory/legal review

### Quality Bar
- Testing requirements
- Performance criteria
- Accessibility compliance

---

## Common Mistakes

### 1. Effort Optimism
Teams chronically underestimate effort. Counter by:
- Using historical data ("Similar feature X took Y weeks")
- Adding buffer (1.5x-2x for new territory)
- Including design, QA, docs, deployment

### 2. Value Inflation
Every feature's sponsor thinks it's high value. Counter by:
- Requiring evidence (data, user research, competitive analysis)
- Using consistent criteria across all items
- Challenging: "Compared to [known high-value feature], how does this rank?"

### 3. Ignoring Big Bets
Quick Wins are tempting, but only Big Bets transform the product. Reserve capacity for strategic work.

### 4. Analysis Paralysis
Don't debate endlessly. If an item is borderline between quadrants, the difference probably doesn't matter. Pick and move on.

### 5. Static Thinking
Value and effort change over time. New information, market shifts, and tech improvements can move items between quadrants. Re-evaluate periodically.

---

## When to Use This Framework

**Good for:**
- Quick team alignment on priorities
- Visual communication with stakeholders
- Early-stage product planning
- Triage of incoming requests

**Not ideal for:**
- Detailed roadmap planning (too coarse)
- Comparing items within the same quadrant (use RICE)
- Technical debt prioritization (different criteria needed)

---

## Combining with Other Frameworks

| Scenario | Add This Framework |
|----------|-------------------|
| Need more granularity | Use RICE scoring within Quick Wins quadrant |
| Want to understand user perception | Overlay Kano categories |
| Stakeholders disagree on criteria | Use Weighted Scoring with explicit weights |
| Need to consider cost of delay | Add WSJF (Weighted Shortest Job First) |

---

## Template Output

After a session, document results:

```markdown
## Quick Wins (Do First)
1. [Feature A] - Value: High, Effort: 1 week - Rationale: ...
2. [Feature B] - Value: High, Effort: 3 days - Rationale: ...

## Big Bets (Plan Next)
1. [Feature C] - Value: High, Effort: 2 months - Rationale: ...
   - Phase 1 scope: ...
   - Dependencies: ...

## Fill-Ins (Opportunistic)
- [Feature D] - Nice-to-have for Q3 if time permits

## Money Pits (Avoid)
- [Feature E] - Revisit if user demand increases
- [Feature F] - Descoped; not solving validated problem
```
