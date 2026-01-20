# Session Summarization Skill

Generate a concise summary of work completed in this session to help a developer pick up where we left off.

## Instructions

1. Review the full conversation context
2. Create a structured summary with the following sections:

```markdown
## Session Summary

**Date:** [Current date]
**Project:** [Project name and path]

### What Was Accomplished
- Bullet points of completed work
- Include file paths for key changes
- Note any commits made (with hashes)

### Current State
- Where did we leave off?
- What's working now that wasn't before?
- Any running processes or servers?

### Next Steps
- What was discussed but not yet implemented?
- Any pending tasks or TODOs?
- Suggested next actions

### Key Decisions Made
- Architecture decisions
- Technology choices
- Trade-offs discussed

### Files Changed
- List of key files created or modified
- Brief note on what each does

### Commands to Resume
- Any setup commands needed
- How to run tests
- How to start the dev server
```

3. After generating the summary, copy it to the clipboard using:
   ```bash
   echo "SUMMARY_CONTENT" | pbcopy
   ```

4. Confirm to the user that the summary has been copied to their clipboard.

## Output Format

Keep the summary scannable - use bullet points, not paragraphs. Focus on actionable information that helps someone resume work quickly.

The summary should be detailed enough to understand context but concise enough to read in under 2 minutes.
