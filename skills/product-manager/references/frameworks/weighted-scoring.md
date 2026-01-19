# ABOUTME: Weighted Scoring framework for custom prioritization criteria.
# ABOUTME: Includes criteria selection, weighting methods, and scoring templates.

# Weighted Scoring Model

## Overview

Weighted Scoring is a flexible prioritization framework where you:
1. Define custom criteria important to your context
2. Assign weights reflecting relative importance
3. Score each feature against each criterion
4. Calculate weighted totals for ranking

Unlike fixed frameworks (RICE, MoSCoW), Weighted Scoring adapts to your specific business needs.

## The Formula

```
Total Score = Σ (Criterion Weight × Feature Score)
```

For each feature:
```
Score = (W₁ × S₁) + (W₂ × S₂) + (W₃ × S₃) + ...
```

Where:
- W = Weight (how important is this criterion?)
- S = Score (how well does this feature meet this criterion?)

---

## Step 1: Define Criteria

Choose 4-7 criteria. More than 7 becomes unwieldy; fewer than 4 may miss important dimensions.

### Common Criteria Categories

**User Value**
- User pain point severity
- Breadth of users affected
- Frequency of use
- User satisfaction impact

**Business Value**
- Revenue impact
- Cost reduction
- Strategic alignment
- Competitive advantage

**Risk & Feasibility**
- Technical complexity
- Team expertise
- Dependencies
- Confidence in estimates

**Constraints**
- Time to market
- Compliance requirements
- Resource availability

### Example Criteria Sets

**For a B2C Mobile App:**
1. User reach (% of users affected)
2. User delight (satisfaction impact)
3. Retention impact
4. Development effort (inverse)
5. Strategic fit

**For a B2B SaaS Product:**
1. Revenue impact
2. Customer retention impact
3. Competitive parity
4. Implementation complexity (inverse)
5. Sales enablement value

**For an Internal Tool:**
1. Time savings
2. Error reduction
3. User adoption likelihood
4. Development cost (inverse)
5. Maintenance burden (inverse)

---

## Step 2: Assign Weights

Weights should sum to 100% (or 1.0) for easy interpretation.

### Methods for Determining Weights

**1. Direct Assignment**
Stakeholders agree on percentages directly.
- Fast but may reflect loudest voice
- Good for small teams with aligned goals

**2. Pairwise Comparison**
Compare each criterion pair: "Is A more important than B?"
- More rigorous
- Reveals hidden disagreements
- Tools: AHP (Analytic Hierarchy Process)

**3. 100-Point Budget**
Give stakeholders 100 points to distribute across criteria.
- Intuitive
- Forces trade-offs
- Average results if multiple stakeholders

### Example Weight Distribution

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Revenue Impact | 30% | Primary business goal |
| User Satisfaction | 25% | Retention driver |
| Strategic Alignment | 20% | Long-term positioning |
| Competitive Parity | 15% | Market necessity |
| Effort (inverse) | 10% | Resource constraint |
| **Total** | **100%** | |

---

## Step 3: Define Scoring Scales

Use consistent scales across criteria. Common options:

### 1-5 Scale (Recommended)
| Score | Meaning |
|-------|---------|
| 5 | Exceptional / Maximum impact |
| 4 | High |
| 3 | Medium |
| 2 | Low |
| 1 | Minimal / None |

### 1-10 Scale
More granular but harder to calibrate.

### Fibonacci (1, 2, 3, 5, 8)
Emphasizes that larger differences matter more.

### Binary (0 or 1)
For yes/no criteria (e.g., "Required for compliance?")

### Inverse Scales
For negative criteria (effort, risk, cost), either:
- Score low = bad (5 = hard, 1 = easy), then subtract from max
- Score inversely (5 = easy, 1 = hard)

---

## Step 4: Score Features

### Calibration
Before scoring all features:
1. Pick 2-3 reference features with known characteristics
2. Score them first to anchor the scale
3. Use as benchmarks ("Is Feature X higher or lower than Reference Y?")

### Scoring Session
- Have multiple scorers to reduce bias
- Discuss scores that differ by >2 points
- Document reasoning for non-obvious scores

### Example Scoring Matrix

| Feature | Revenue (30%) | Satisfaction (25%) | Strategic (20%) | Competitive (15%) | Effort* (10%) | Total |
|---------|--------------|-------------------|-----------------|-------------------|---------------|-------|
| Feature A | 4 | 5 | 3 | 2 | 4 | 3.85 |
| Feature B | 5 | 3 | 4 | 5 | 2 | 3.95 |
| Feature C | 2 | 4 | 5 | 3 | 5 | 3.55 |
| Feature D | 3 | 2 | 2 | 4 | 3 | 2.70 |

*Effort inverted: 5 = low effort, 1 = high effort

**Calculations:**
- Feature A: (0.30×4) + (0.25×5) + (0.20×3) + (0.15×2) + (0.10×4) = 3.85
- Feature B: (0.30×5) + (0.25×3) + (0.20×4) + (0.15×5) + (0.10×2) = 3.95

---

## Interpreting Results

### Ranking
Higher scores = higher priority. But don't treat small differences as meaningful.

**Score bands:**
- 4.0+ = High priority
- 3.0-3.9 = Medium priority
- <3.0 = Low priority / revisit

### Sensitivity Analysis
Check if results change significantly when:
- Weights shift ±10%
- Borderline scores change by 1 point

If results are fragile, the features are truly close in priority.

### Outliers
Investigate features with:
- Very high scores (validate assumptions)
- Very low scores (should they be deprioritized?)
- High variance across criteria (trade-off decisions needed)

---

## When to Use Weighted Scoring

**Good for:**
- Complex decisions with multiple stakeholders
- When standard frameworks don't capture your context
- Transparent, defensible prioritization
- Organizations that value data-driven decisions

**Not ideal for:**
- Quick triage (use MoSCoW or Value/Effort)
- Very early-stage exploration (criteria not yet known)
- Small backlogs (<10 items) — overkill

---

## Common Mistakes

### 1. Too Many Criteria
More than 7 criteria dilutes the signal. Combine related criteria.

### 2. Unvalidated Weights
Weights should reflect actual priorities, not aspirational ones. Test against past decisions.

### 3. Inconsistent Scoring
Without calibration, one person's "4" is another's "3". Use reference features.

### 4. Ignoring Qualitative Factors
The model is a tool, not a decision. Override when judgment demands it—just document why.

### 5. Gaming the System
If stakeholders know the weights, they may inflate scores strategically. Use blind scoring or calibration checks.

---

## Spreadsheet Template

```
| Feature | [Criterion 1] | [Criterion 2] | [Criterion 3] | [Criterion 4] | Total | Rank |
|         | Weight: X%    | Weight: X%    | Weight: X%    | Weight: X%    |       |      |
|---------|---------------|---------------|---------------|---------------|-------|------|
| Feature A | [1-5] | [1-5] | [1-5] | [1-5] | =SUMPRODUCT | |
| Feature B | [1-5] | [1-5] | [1-5] | [1-5] | =SUMPRODUCT | |
| Feature C | [1-5] | [1-5] | [1-5] | [1-5] | =SUMPRODUCT | |
```

Formula for Total (Google Sheets/Excel):
```
=SUMPRODUCT(B2:E2, $B$1:$E$1)
```
Where row 1 contains weights as decimals (0.30, 0.25, etc.)

---

## Combining with Other Frameworks

| Scenario | Combination |
|----------|-------------|
| Need quick initial triage | MoSCoW first, then Weighted Scoring on Must/Should Haves |
| Want to understand user perception | Use Kano categories as one criterion |
| Comparing within a category | Use RICE for detailed scoring within a priority tier |
| Stakeholders disagree on criteria | Run weight-setting exercise before scoring |
