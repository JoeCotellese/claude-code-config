# Workflow 2: Process Inbox

## Trigger Phrases
- "Let's process my inbox"
- "Help me organize my tasks"
- "Let's go through my todo list"
- "Process my inbox"

## Process

1. **Fetch all inbox items from Todoist:**
   ```
   mcp__todoist__find-tasks with:
     projectId: "6CrffChVJmwxG79h",  # Inbox project
     limit: 50
   ```

   Show count and begin processing (see Sample Output below).

2. For each item, follow the GTD clarification workflow:

   a. **Present item with suggested rewrite:**
      - Show original: "[original task text]"
      - Analyze and suggest improvement if needed:
        - Make vague items specific and actionable
        - Add verb if missing (Buy, Call, Email, Write, etc.)
        - Add context that helps future self understand
        - Clarify ambiguous references
      - Ask: "Use this rewrite or keep original?"
      - Update task content if changed using `mcp__todoist__update-tasks`

   **Rewrite examples:**
   - "Kids sketcher socks" → "Buy Kids Skechers socks"
   - "Mom's birthday" → "Plan gift for Mom's birthday"
   - "What Kurt Cobain taught me" → "Blog post idea: What Kurt Cobain taught me about vibecoding"
   - "Check on project" → "Check on NEXTGRES project status"

   b. **Understand it:** "Let's look at: [item]. What is this about?" (if unclear from rewrite)

   c. **Is it actionable?**
      - **NO** →
        - Reference info? → Suggest user save to Obsidian `2_Literature Notes/` or `3_Permanent Notes/`, then delete from Todoist
        - Someday? → Move to Someday/Maybe project using `mcp__todoist__update-tasks`
        - Not needed? → Delete using `mcp__todoist__delete-object`

      - **YES** →
        - **< 2 minutes?** → User does it now, then mark complete using `mcp__todoist__complete-tasks`
        - **Single action?** →
          - Blocked? → Move to Waiting For project, add waiting context in description
          - Ready? → Move to Next Actions project + add metadata (see Metadata Collection below)
        - **Multiple steps (project)?** →
          - Ask: "What's the desired outcome?"
          - Create Obsidian project note in `/Users/joec/obsidian-vault/4_Projects/[ProjectName].md` with standard template
          - Generate Obsidian URI link: `obsidian://open?vault=obsidian-vault&file=4_Projects%2F[ProjectName]`
          - Create task in Projects project with outcome as description and Obsidian link
          - Inform user: "I've created a project: [title] with documentation in Obsidian"
          - Ask: "What actions do you need to take for this project?"
          - Capture ALL next actions in the Obsidian project note's `## Next Actions` section
          - Ask: "Which one should we tackle first?"
          - Create ONLY that first action in Todoist Next Actions with metadata and link to project
          - Note: Remaining actions stay in Obsidian as the backlog

3. Continue until inbox is empty

## Sample Output

**Starting inbox processing:**
```
┌─────────────────────────────────────────────────────────────┐
│  📥 INBOX PROCESSING                                        │
└─────────────────────────────────────────────────────────────┘

  Found 12 items in your inbox. Let's process them.
```

**Processing an item:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [1/12]

  Original:  "Kids sketcher socks"

  Rewrite:   "Buy Kids Skechers socks"
             └─ Added verb, fixed spelling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [k]eep rewrite  │  [e]dit  │  [d]elete  │  [s]kip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**After keeping — collect metadata:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [1/12]

  Task: "Buy Kids Skechers socks"

── Metadata ─────────────────────────────────────────────────

  Inferred:  @errands  │  ○ low  │  15m

  Accept these? Or adjust:

─────────────────────────────────────────────────────────────
  [y]es, accept  │  [c]ontext  │  [e]nergy  │  [t]ime
```

**Item moved to Next Actions:**
```
  ✓ Added to Next Actions: "Buy Kids Skechers socks"
    └─ ○ low  │  15m  │  @errands
```

**Item moved to Someday/Maybe:**
```
  → Moved to Someday/Maybe: "Learn to play piano"
```

**Item deleted:**
```
  ✕ Deleted: "Old reminder that no longer applies"
```

**Creating a project:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [5/12]

  Task: "Plan kitchen renovation"

  This looks like a multi-step project.

── Project Setup ────────────────────────────────────────────

  ✓ Created project note in Obsidian
    📄 obsidian://open?vault=obsidian-vault&file=4_Projects%2FKitchen%20Renovation

  What's the first action to take?
```

**End of processing:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ INBOX COMPLETE                                           │
└─────────────────────────────────────────────────────────────┘

── Summary ──────────────────────────────────────────────────

  Processed:  12 items
  ✓ Kept:      5 → Next Actions
  → Moved:     3 → Someday/Maybe
  ⏳ Waiting:   1 → Waiting For
  📁 Projects:  1 created
  ✕ Deleted:   2

  Inbox: 0 items remaining ✓
```

## Output Components Used

- **Section Header** — `📥 INBOX PROCESSING`
- **Progress indicator** — `[1/12]` counter
- **Inbox Item Card** — Original, rewrite, action options
- **Subsection header** — `── Metadata ──`
- **Confirmation messages** — `✓` `→` `✕` for different outcomes
- **Summary statistics** — End-of-workflow totals
- **Action footer** — Available commands at each step

## Metadata Collection for Next Actions

When moving an item to Next Actions, use smart inference + confirmation:

### Step 1: Infer metadata from task content

Analyze the task and infer likely values using these patterns:

**Context inference:**
- Keywords like "book", "search", "email", "write" → `@computer`
- Keywords like "call", "text" → `@phone`
- Keywords like "buy", "pick up", "drop off", "renew" → `@errands`
- Keywords like "fix", "clean", "organize" + home context → `@home`
- Work-related keywords or project names → `@work`
- Unclear or flexible → `@anywhere`

**Energy inference:**
- Creative work, strategic thinking, writing, coding → `⚡` high
- Meetings, planning, research, data entry → `◐` medium
- Admin tasks, booking, simple lookups, errands → `○` low

**Time inference:**
- "Quick", "check", "look up" → `5m`
- "Call", "book", "send email" → `15m`
- "Write", "research", "plan" → `30m` to `1h`
- "Deep work", "analyze", "design" → `1h` to `2h`

### Step 2: Confirm with user

Present inferred values and let user accept or adjust.

### Step 3: Apply metadata and move to Next Actions

Update task with confirmed metadata and move to Next Actions:
```
mcp__todoist__update-tasks with:
  tasks: [{
    id: "task-id",
    projectId: "6fHPx2qmvwhq5x4X",  # Next Actions
    labels: ["@computer", "#energy-medium"],
    duration: "30m"
  }]
```
