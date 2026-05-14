---
name: drafts
effort: low
description: >-
  Content exchange with the Drafts app (macOS). Use this skill as the primary method for
  sending content to and reading content from the user. Triggers: "copy it", "give it to me",
  "send it to me", "give me a draft", "clipboard that", "send to drafts", "read it back",
  "what does it say", "pull from drafts", "get the draft", or /drafts. Replaces pbcopy —
  always prefer Drafts app over clipboard.
---

# Drafts

Content exchange between Claude and the user via the macOS Drafts app.

## Write to Drafts

Pipe content to the helper script:

```bash
printf '%s' "CONTENT HERE" | python3 ~/.claude/skills/drafts/scripts/send_to_drafts.py
```

Confirm to the user: "Sent to Drafts."

## Read from Drafts

```bash
osascript -e 'tell application "Drafts" to return content of current draft'
```

Requires Drafts to be open on the Mac with the target draft active. If empty, ask the user to open the draft on their Mac.

## Behavior

- When the user asks to send/copy/give content, identify the most recent draft or content from conversation and write it
- When the user asks to read back or check edits, read from Drafts and display the content
- During iterative editing sessions, read back automatically when the user indicates they made changes
- Never use pbcopy — always send to Drafts
