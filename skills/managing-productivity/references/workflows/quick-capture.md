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

2. Confirm capture: "Captured: '[task description]' to your inbox. Want to process it now or leave it for later?"

3. If user says "now" → Enter Workflow 2 for just that item
4. If user says "later" → "Got it. It'll be there when you process your inbox next."

## Implementation Notes

- Capture should be FAST - don't ask clarifying questions during capture
- Always capture to Inbox first
- Clarify and add metadata later during processing
