# ABOUTME: MoSCoW prioritization framework reference for requirements triage.
# ABOUTME: Includes category definitions, timeboxing technique, and stakeholder alignment.

# MoSCoW Prioritization

## Overview

MoSCoW is a prioritization technique that categorizes requirements into four groups:
- **M**ust have
- **S**hould have
- **C**ould have
- **W**on't have (this time)

Developed by Dai Clegg at Oracle, it's widely used in agile and timeboxed projects to ensure the most critical requirements are delivered first.

## The Four Categories

### Must Have
**Non-negotiable requirements for this release.**

- Without these, the release has no value
- If even one Must Have isn't delivered, the release fails
- Should represent ~60% of effort in a timebox

**Questions to determine Must Have:**
- Will the product be unusable without this?
- Is there a legal/regulatory requirement?
- Is there a contractual obligation?
- Will a key user segment abandon the product without this?

**Examples:**
- Login functionality for an authentication system
- GDPR compliance for EU launch
- Core checkout flow for an e-commerce site

### Should Have
**Important but not critical for this release.**

- Significantly add value
- May have a workaround (even if painful)
- Should represent ~20% of effort in a timebox

**Questions to determine Should Have:**
- Is there a temporary workaround?
- Can we launch without this and add it quickly after?
- Would most users be disappointed but not blocked?

**Examples:**
- Password reset via email (workaround: contact support)
- Bulk import feature (workaround: manual entry)
- Dark mode (workaround: use default theme)

### Could Have
**Desirable but not necessary.**

- Nice to have if time permits
- First to be dropped if schedule slips
- Should represent ~20% of effort in a timebox

**Questions to determine Could Have:**
- Is this mostly polish or convenience?
- Would only a subset of users notice this?
- Does this improve experience but not enable core functionality?

**Examples:**
- Animated transitions
- Advanced filtering options
- Social sharing features

### Won't Have (This Time)
**Explicitly out of scope for this release.**

- Acknowledged as valuable, but deferred
- Prevents scope creep
- Creates a backlog for future releases

**Questions to determine Won't Have:**
- Is this valuable but not urgent?
- Does this require dependencies we don't have?
- Is this speculative (unvalidated user need)?

**Examples:**
- Mobile app (launching web-only first)
- Multi-language support (US market first)
- AI-powered recommendations (post-MVP)

---

## The 60-20-20 Rule

In timeboxed projects, allocate effort as:

| Category | % of Effort | Purpose |
|----------|-------------|---------|
| Must Have | 60% | Ensures delivery of essentials |
| Should Have | 20% | Adds significant value |
| Could Have | 20% | Buffer for unknowns |

**Why this ratio?**
- If everything goes perfectly, you deliver 100%
- If you hit problems, Could Haves get dropped first (still 80% delivered)
- If severe problems, Should Haves get deferred (still 60% of critical value delivered)

---

## Running a MoSCoW Session

### Preparation

1. **Define the timebox** - What's the deadline and team capacity?
2. **List all requirements** - Features, user stories, or tasks
3. **Estimate effort** - T-shirt sizes or story points per item
4. **Identify stakeholders** - Who has authority to prioritize?

### Session Format (60-90 minutes)

**1. Set Context (10 min)**
- Review deadline and constraints
- Clarify the 60-20-20 rule
- Agree on definition of "Must Have" (legal, usability, etc.)

**2. Initial Sort (20 min)**
- Each stakeholder silently categorizes items
- Use sticky notes or voting dots

**3. Review Must Haves (20 min)**
- Go through all items marked Must Have
- Challenge each: "Will the release fail without this?"
- Move questionable items to Should Have
- Total effort should be ~60% of capacity

**4. Review Should/Could (15 min)**
- Ensure Should Haves are truly important
- Check that Could Haves fit in remaining 40%
- Move overflow to Won't Have

**5. Confirm Won't Haves (10 min)**
- Explicitly list what's out of scope
- Capture rationale for future reference
- Set expectations with stakeholders

**6. Document (5 min)**
- Record final categorization
- Note any disagreements or risks

---

## Example: E-Commerce MVP

| Requirement | Category | Rationale |
|-------------|----------|-----------|
| Product catalog browsing | Must | Core functionality |
| Shopping cart | Must | Core functionality |
| Checkout with Stripe | Must | Revenue-critical |
| User accounts | Must | Required for orders |
| Password reset | Should | Workaround: support ticket |
| Order history | Should | Users expect, but can check email |
| Wishlist | Could | Nice to have, not essential |
| Product reviews | Could | Valuable but not for MVP |
| Apple Pay | Won't | Post-launch enhancement |
| Multi-currency | Won't | US market first |

---

## When to Use MoSCoW

**Good for:**
- Timeboxed releases with hard deadlines
- Stakeholder alignment on what's in/out
- Projects with more requirements than capacity
- Agile sprints and release planning

**Not ideal for:**
- Comparing individual features (use RICE)
- Long-term roadmap planning
- Technical debt prioritization

---

## Common Mistakes

### 1. Everything is Must Have
If >60% of items are Must Have, you're not prioritizing.
- Challenge: "Will the release fail without this?"
- Force rank Must Haves if needed

### 2. Won't Have = Never
Won't Have means "not this release," not "never." Communicate this clearly to avoid disappointment.

### 3. Ignoring Effort
A small Must Have is different from a huge Must Have. Weight by effort to validate the 60-20-20 allocation.

### 4. No Stakeholder Buy-In
If key stakeholders don't agree with Must Haves, you'll face pressure later. Get explicit agreement.

### 5. Skipping Won't Have
Without explicit Won't Haves, scope creeps in. Document what's out to prevent "can we just add one more thing?"

---

## MoSCoW vs. Other Frameworks

| Framework | Best For | MoSCoW Difference |
|-----------|----------|-------------------|
| RICE | Scoring and ranking | MoSCoW categorizes, RICE ranks |
| Value/Effort | Visual quadrant view | MoSCoW is simpler, no 2x2 grid |
| Kano | Understanding satisfaction drivers | MoSCoW is about delivery scope |
| Weighted Scoring | Custom criteria | MoSCoW has fixed categories |

**Combining frameworks:**
- Use MoSCoW to define scope, then RICE to rank within Must Haves
- Use Kano to understand value, then MoSCoW to triage for a release

---

## Template Output

After a MoSCoW session, document:

```markdown
## Release: [Name] - Target: [Date]

### Must Have (60% effort - ~X weeks)
- [Requirement A] - X points
- [Requirement B] - X points
- [Requirement C] - X points

### Should Have (20% effort - ~X weeks)
- [Requirement D] - X points
- [Requirement E] - X points

### Could Have (20% effort - ~X weeks)
- [Requirement F] - X points
- [Requirement G] - X points

### Won't Have (This Release)
- [Requirement H] - Rationale: ...
- [Requirement I] - Rationale: ...

### Risks
- If [risk], [Should Have X] may be deferred
- [Requirement Y] has uncertain estimate, may impact Could Haves
```
