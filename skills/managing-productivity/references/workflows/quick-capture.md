# Workflow 3: Quick Capture

## Trigger Phrases
- "Add task: [description]"
- "Capture: [description]"
- "Remind me to [description]"
- "Add to my inbox: [description]"
- "Todo: [description]"

## Process

1. Create task directly in Todoist Inbox:
   ```
   mcp__todoist__add-tasks with:
     tasks: [{
       content: "[description]",
       projectId: "6CrffChVJmwxG79h"  # Inbox
     }]
   ```

2. Confirm capture (see Sample Output below)

3. If user says "now" → Enter Workflow 2 for just that item
4. If user says "later" → End workflow

## Sample Output

**After capture:**
```
  ✓ Captured: "Call mom about birthday plans"
    └─ Added to Inbox

─────────────────────────────────────────────────────────────
  [p]rocess now  │  [l]ater
```

**If user chooses "process now":**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Task: "Call mom about birthday plans"

── Metadata ─────────────────────────────────────────────────

  Inferred:  @phone  │  ○ low  │  15m

  Accept these? Or adjust:

─────────────────────────────────────────────────────────────
  [y]es, accept  │  [c]ontext  │  [e]nergy  │  [t]ime
```

**If user chooses "later":**
```
  Got it. It'll be there when you process your inbox next.
```

## Output Components Used

- **Confirmation message** — `✓ Captured: "[task]"`
- **Action footer** — Process now or later options
- **Metadata section** — When processing immediately (reuses inbox components)

## Implementation Notes

- Capture should be FAST - don't ask clarifying questions during capture
- Always capture to Inbox first
- Clarify and add metadata later during processing
- One-line confirmation keeps the flow quick
