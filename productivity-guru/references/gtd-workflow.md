# GTD Clarification Workflow

This reference provides the detailed decision tree for processing inbox items according to GTD methodology.

## Processing Questions (In Order)

For each item in the inbox ("Todo List"), ask these questions in sequence:

### 1. What is it?
Understand the nature of the captured item. Ask the user to explain if unclear from the title alone.

### 2. Is it actionable?

#### If NO (not actionable):
- **Is it reference information?** → Move to "Reference" list
- **Might you want to do it someday?** → Move to "Someday/Maybe" list
- **Not needed at all?** → Delete it

#### If YES (actionable):

##### 2a. Can it be done in less than 2 minutes?
- **YES** → Do it now (or tell user to do it now), then mark complete
- **NO** → Continue to next question

##### 2b. Is it a single action or multiple steps?

###### Single Action Path:
- **Am I the right person to do this?**
  - **NO** → Delegate (user should handle delegation, can track in "Waiting For")
  - **YES** → Continue

- **Can I do this now?**
  - **Blocked on someone/something?** → Move to "Waiting For" with note about what you're waiting for
  - **Can do when ready** → Move to "Next Actions" and add metadata (see below)

###### Multiple Steps (Project) Path:
- Ask: "What's the desired outcome?" (This becomes the project title)
- Create item in "Projects" list
- Inform user: "I've created a project in your Projects list"
- Ask: "What's the very next physical action to move this forward?"
- Create that action in "Next Actions" with proper metadata

## Next Actions Metadata

When moving an item to "Next Actions", gather and add this information to the reminder's notes field:

### Required Metadata:
1. **Context Tag** - Where/how can this be done?
   - `@home` - At home
   - `@work` - At work/office
   - `@computer` - Requires computer
   - `@phone` - Phone calls
   - `@errands` - Out and about
   - `@anywhere` - Can be done anywhere

2. **Energy Tag** - Mental/physical energy required:
   - `#energy-high` - Deep work, creative thinking, complex problem-solving
   - `#energy-medium` - Routine work, meetings, moderate focus
   - `#energy-low` - Administrative, simple tasks, organizing

3. **Time Tag** - Estimated time to complete:
   - `#time-5m` - 5 minutes
   - `#time-15m` - 15 minutes
   - `#time-30m` - 30 minutes
   - `#time-1h` - 1 hour
   - `#time-2h` - 2 hours or more

### Optional Metadata:
4. **Priority** - Use Apple Reminders priority (1-9, where 9 is highest)
   - Ask about importance and urgency

5. **Due Date** - When must this be done?
   - Only set if there's a real deadline
   - GTD philosophy: Most next actions don't have hard deadlines

## Example Processing Session

**Item:** "Website redesign"

**Q:** What is this about?
**A:** We need to update our company website with a new design.

**Q:** Is this actionable?
**A:** Yes

**Q:** Can you do it in less than 2 minutes?
**A:** No, it's a bigger project

**Q:** Is this a single action or multiple steps?
**A:** Multiple steps - it's a whole project

**Q:** What's the desired outcome?
**A:** Launch a redesigned website that's modern and mobile-friendly

→ Create project: "Launch redesigned company website"
→ Inform user: "I've created a project in your Projects list: 'Launch redesigned company website'"

**Q:** What's the very next physical action to move this forward?
**A:** Email the designer to schedule a kickoff meeting

→ Create in Next Actions: "Email Sarah to schedule website redesign kickoff"

**Q:** What context does this require?
**A:** @computer

**Q:** What energy level?
**A:** Low - it's just a quick email

**Q:** How long will it take?
**A:** About 10 minutes

**Q:** Is there a deadline?
**A:** Would be good to do this week, but not critical

**Q:** Priority level?
**A:** Medium priority

→ Final reminder in "Next Actions":
- Title: "Email Sarah to schedule website redesign kickoff"
- Notes: "@computer #energy-low #time-10m"
- Priority: 5 (medium)
- Due date: None (no hard deadline)

## Tips for Efficient Processing

- Process top to bottom, don't skip around
- Make decisions quickly - don't overthink
- The goal is to empty the inbox, not perfect categorization
- When in doubt about energy/time, estimate and move on
- Projects should have at least one next action at all times
- If a project has no next action, it might belong in Someday/Maybe
