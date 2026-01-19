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

   Show count: "Found X items in your inbox. Let's process them one by one."

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
- Creative work, strategic thinking, writing, coding → `#energy-high`
- Meetings, planning, research, data entry → `#energy-medium`
- Admin tasks, booking, simple lookups, errands → `#energy-low`

**Time inference:**
- "Quick", "check", "look up" → `5m`
- "Call", "book", "send email" → `15m`
- "Write", "research", "plan" → `30m` to `1h`
- "Deep work", "analyze", "design" → `1h` to `2h`

### Step 2: Confirm with user via AskUserQuestion

Use the AskUserQuestion tool with inferred defaults pre-selected:

```
AskUserQuestion with 3 questions:
1. Context (header: "Context", pre-select inferred value)
   - @computer, @phone, @errands, @home, @work, @anywhere

2. Energy (header: "Energy", pre-select inferred value)
   - high (deep work), medium (routine), low (admin)

3. Time (header: "Duration", pre-select inferred value)
   - 5m, 15m, 30m, 1h, 2h
```

User can quickly accept defaults or adjust as needed.

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
