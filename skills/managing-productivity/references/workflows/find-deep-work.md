# Workflow 7: Find Deep Work Time

## Trigger Phrases
- "When can I do deep work?"
- "Find time for focused work"
- "Show me blocks for high-energy tasks"
- "When should I work on [high-energy task]?"

## Process

1. Check calendar for this week:
   - Use calendar MCP to fetch 7-day range from today
   - Find free blocks of 2+ hours (ideal for deep work)
   - Prioritize morning/early morning slots (before noon, especially before 9am)

2. Search Next Actions for #energy-high tasks:
   ```
   mcp__todoist__find-tasks with:
     projectId: "6fHPx2qmvwhq5x4X",  # Next Actions
     labels: ["#energy-high"],
     limit: 20
   ```
   Sort by duration (longest first, as they benefit most from deep work blocks)

3. Present available deep work slots with task suggestions:
   ```
   Here are your best deep work blocks this week:

   **Tuesday, Nov 14**
   - 8:00 AM - 11:00 AM (3 hours free) - Prime time
     Suggested: Update EyeGuide video API (2h) @computer #energy-high

   **Thursday, Nov 16**
   - 9:00 AM - 12:00 PM (3 hours free) - Prime time
     Suggested: Look at Shopify APIs (1h) @computer #energy-high

   **Friday, Nov 17**
   - 2:00 PM - 5:00 PM (3 hours free)
     Available for deep work

   Want me to schedule any of these tasks?
   ```

4. If user says yes:
   - Enter Workflow 6 (Schedule Time for Task) for the chosen task

## Implementation Notes

- Define "deep work blocks" as 2+ hours of continuous free time
- Morning blocks (before noon) are "prime time" and should be highlighted
- If no 2+ hour blocks available, suggest the longest available blocks with a note: "No full deep work blocks available, but here are your longest stretches"
- Consider back-to-back 1-hour blocks as viable for deep work if there's no meeting between them

---

## Sample Output

### Deep Work Slots Found

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 DEEP WORK SLOTS THIS WEEK                               │
└─────────────────────────────────────────────────────────────┘

  Found 3 blocks of 2+ hours for focused work.

── Tuesday, Mar 6 ───────────────────────────────────────────
   8:00 - 11:00  ○ FREE (3h)                  ★ Prime time
                 ▸ Update EyeGuide video API           ⚡  2h

── Thursday, Mar 8 ──────────────────────────────────────────
   9:00 - 12:00  ○ FREE (3h)                  ★ Prime time
                 ▸ Look at Shopify APIs                ⚡  1h

── Friday, Mar 9 ────────────────────────────────────────────
   2:00 -  5:00  ○ FREE (3h)
                 └─ Available for deep work

── High-Energy Tasks ────────────────────────────────────────
  1 │ Update EyeGuide video API               ⚡    2h   @computer
  2 │ Look at Shopify APIs                    ⚡    1h   @computer
  3 │ Design database schema                  ⚡   90m   @computer

─────────────────────────────────────────────────────────────
  [1-3] Schedule task  │  [m]ore tasks  │  [d]one
```

### No Deep Work Blocks Available

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 DEEP WORK SLOTS THIS WEEK                               │
└─────────────────────────────────────────────────────────────┘

  ⚠ No full deep work blocks (2+ hours) available this week.

── Longest Available Stretches ──────────────────────────────
  1 │ Tue  10:00 - 11:30  ○ FREE (1.5h)
  2 │ Wed   2:00 -  3:30  ○ FREE (1.5h)
  3 │ Fri   9:00 - 10:00  ○ FREE (1h)              ★ Morning

  Consider rescheduling meetings to create larger blocks,
  or break down your ⚡ high-energy tasks into smaller chunks.

─────────────────────────────────────────────────────────────
  [1-3] Schedule task  │  [n]ext week  │  [d]one
```

## Output Components Used

- **Section Header** — `🎯 DEEP WORK SLOTS THIS WEEK`
- **Subsection headers** — Day headers, `── High-Energy Tasks ──`
- **Free block display** — Time range, duration, prime time marker
- **Task suggestions** — Indented under matching slots
- **Prime time marker** — `★` for morning blocks
- **Task list** — Numbered high-energy tasks with metadata
- **Warning callout** — `⚠` for no blocks available
- **Action footer** — Available commands
