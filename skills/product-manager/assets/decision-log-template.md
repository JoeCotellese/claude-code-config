
# Prioritization Decision Log
Use this template to document important prioritization decisions and their rationale. This creates a historical record for future reference and helps teams understand why certain decisions were made.

---

## Decision: [Feature/Initiative Name]

**Date:** [Date]
**Decision Maker(s):** [Names]
**Status:** [Approved / Deferred / Rejected]

### Context

**What is being decided:**
[Brief description of the feature or initiative]

**Why this decision was needed:**
[What triggered this prioritization discussion?]

**Stakeholders involved:**
[Who has interest in this decision?]

---

### Options Considered

#### Option A: [Name/Description]
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Estimated Effort:** [T-shirt size or weeks]

#### Option B: [Name/Description]
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Estimated Effort:** [T-shirt size or weeks]

#### Option C: Do Nothing / Defer
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

---

### Decision

**Selected Option:** [Option X]

**Rationale:**
[Why this option was chosen over alternatives. Include specific data points, user feedback, business considerations, and strategic alignment.]

**Trade-offs Accepted:**
[What are we giving up by choosing this option?]

**Risks Acknowledged:**
[What could go wrong? How will we monitor?]

---

### Impact

**What changes:**
- [Change 1]
- [Change 2]

**What doesn't change:**
- [Item 1]
- [Item 2]

**Who is affected:**
- [Stakeholder/Team 1]: [How affected]
- [Stakeholder/Team 2]: [How affected]

---

### Success Criteria

**How we'll know this was the right decision:**
- [Metric 1]: [Target]
- [Metric 2]: [Target]

**Review date:** [When to revisit this decision]

---

### Dissenting Views

[Document any strong disagreements and the reasoning behind them. This is important for understanding the full picture later.]

**[Name]:** [Their perspective]

**[Name]:** [Their perspective]

---

## Example Entry

### Decision: Defer Multi-Language Support

**Date:** 2024-03-15
**Decision Maker(s):** Sarah (PM), James (Eng Lead), Maria (CEO)
**Status:** Deferred to Q3

### Context

**What is being decided:**
Whether to add multi-language support (starting with Spanish, French, German) in Q2.

**Why this decision was needed:**
Multiple enterprise prospects have requested localization. Sales team flagged as blocker for EMEA expansion.

**Stakeholders involved:**
- Sales (requesting for deals)
- Engineering (implementation)
- Marketing (launch coordination)
- Customer Success (support implications)

### Options Considered

#### Option A: Full Localization Q2
**Pros:**
- Unblocks 3 enterprise deals worth $240K ARR
- Competitive parity with main competitor

**Cons:**
- 8 weeks of engineering time
- Delays mobile app v2 launch
- Ongoing maintenance burden

**Estimated Effort:** 8 weeks (2 engineers)

#### Option B: Defer to Q3
**Pros:**
- Mobile v2 ships on time (higher user impact)
- More time to properly architect translation system
- Can hire dedicated localization resource

**Cons:**
- May lose 1-2 enterprise deals
- Competitor widens gap in EMEA

**Estimated Effort:** Same, just later

#### Option C: MVP Localization (UI only, no content)
**Pros:**
- Faster (4 weeks)
- May satisfy some prospects

**Cons:**
- Incomplete experience frustrates users
- Technical debt for full solution later

### Decision

**Selected Option:** Option B - Defer to Q3

**Rationale:**
Mobile v2 affects 100% of users vs. localization affecting ~5% potential users. The enterprise deals, while valuable, are not certain to close even with localization. Architectural concerns about doing localization quickly suggest a more thoughtful approach will save time long-term.

**Trade-offs Accepted:**
- May lose 1-2 enterprise deals worth ~$150K ARR
- Competitor gains 3-month advantage in EMEA

**Risks Acknowledged:**
- If we lose the deals, we'll know by end of Q2
- Sales team may escalate; CEO has agreed to this decision

### Impact

**What changes:**
- Mobile v2 remains Q2 priority
- Localization moves to Q3 roadmap
- Sales team given talking points for prospects

**Who is affected:**
- Sales: Need to manage prospect expectations
- Engineering: No change to Q2 plan
- Marketing: EMEA launch delayed

### Success Criteria

- Mobile v2 launches by May 15
- Localization ready by August 1
- Track lost deals attributed to localization gap

**Review date:** June 1 (Q2 deal outcomes known)

### Dissenting Views

**Tom (Sales Lead):** Strongly advocated for Option A. Believes the enterprise deals are higher value than mobile improvements for existing users. Concerned about competitive pressure in EMEA. Agreed to support decision after CEO weighed in.

---

## Log Index

| Date | Decision | Status | Key Rationale |
|------|----------|--------|---------------|
| | | | |
| | | | |
| | | | |
