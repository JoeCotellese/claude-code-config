# Workflow 4: Project Check-in

## Trigger Phrases
- "What's the status of [project]?"
- "Show me my projects"
- "What projects am I working on?"
- "Check in on [project name]"

## Process

1. Search Todoist Projects project:
   ```
   mcp__todoist__find-tasks with:
     projectId: "6fHPx2qMxx45cVm3",  # Projects
     limit: 50
   ```

2. If specific project requested:
   - Find the project task
   - Search Next Actions for tasks that reference this project (via description or labels)
   - Search Waiting For for blocked items related to this project
   - Check if Obsidian project note exists in `4_Projects/[ProjectName].md`
   - Present using project card format (see Sample Output below)

3. If showing all projects:
   - List all project tasks from Projects project
   - For each, show basic status
   - Identify any projects without next actions (stalled)

## Sample Output

**Single project check-in:**
```
┌─────────────────────────────────────────────────────────────┐
│  📁 PROJECT: Kitchen Renovation                             │
└─────────────────────────────────────────────────────────────┘

── Desired Outcome ──────────────────────────────────────────

  Complete kitchen renovation with new cabinets, countertops,
  and appliances by end of Q2.

── Next Actions ─────────────────────────────────────────────

  # │ Task                                  Energy  Time   Status
 ───┼────────────────────────────────────────────────────────────
  1 │ Get quotes from 3 contractors            ◐    1h    ☐ active
  2 │ Research countertop materials            ◐   30m    ☐ in backlog

── Waiting For ──────────────────────────────────────────────

  ⏳ Contractor A to send revised quote (requested Mar 1)
  ⏳ Landlord approval for cabinet changes (requested Feb 28)

── Documentation ────────────────────────────────────────────

  📄 obsidian://open?vault=obsidian-vault&file=4_Projects%2FKitchen%20Renovation

─────────────────────────────────────────────────────────────
  [a]dd action  │  [w]aiting for  │  [d]one
```

**All projects overview:**
```
┌─────────────────────────────────────────────────────────────┐
│  📁 ACTIVE PROJECTS                                         │
└─────────────────────────────────────────────────────────────┘

  # │ Project                    Next Action           Waiting
 ───┼────────────────────────────────────────────────────────────
  1 │ Kitchen Renovation         Get contractor quotes     2
  2 │ Q1 Performance Review      Draft self-assessment     0
  3 │ Learn Italian              Complete Duolingo unit    0
  4 │ Website Redesign           —                         1  ⚠ stalled

── Summary ──────────────────────────────────────────────────

  Active: 4 projects  │  Stalled: 1  │  Waiting: 3 items total

─────────────────────────────────────────────────────────────
  [1-4] View details  │  [s]talled only  │  [a]dd project
```

**Stalled project alert:**
```
  ⚠ "Website Redesign" has no next actions

  This project may be stalled. Options:

─────────────────────────────────────────────────────────────
  [d]efine next action  │  [s]omeday/maybe  │  [c]omplete project
```

## Output Components Used

- **Section Header** — `📁 PROJECT: [Name]` or `📁 ACTIVE PROJECTS`
- **Subsection headers** — `── Desired Outcome ──`, `── Next Actions ──`, etc.
- **Task table** — Aligned columns for multiple tasks
- **Waiting For list** — `⏳` icon with item and date
- **Warning indicator** — `⚠ stalled` for projects without next actions
- **Summary statistics** — Project counts, waiting items
- **Action footer** — Available commands

## Stalled Project Detection

A project is stalled when:
- It has no tasks in Next Actions
- It has no tasks in Waiting For
- The Obsidian backlog is empty or all items are checked

When detected, prompt: "This project has no next actions. Should we define one, or move it to someday-maybe?"
