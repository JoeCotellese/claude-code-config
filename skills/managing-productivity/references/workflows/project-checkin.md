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
   - Present summary:
     ```
     Project: [Project Name]
     Desired Outcome: [from task description]

     Next Actions:
     - [Action 1 from Next Actions project]
     - [Action 2]

     Waiting For:
     - [Blocked item from Waiting For project]

     Documentation: [Link to Obsidian note if exists]
     ```

3. If showing all projects:
   - List all project tasks from Projects project
   - For each, show basic status
   - Identify any projects without next actions (stalled)

## Stalled Project Detection

If a project has no next actions, ask: "This project has no next actions. Should we define one, or move it to someday-maybe?"
