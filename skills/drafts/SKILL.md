---
name: drafts
effort: low
description: >-
  Content exchange with the user via the Drafts app (macOS) using the `drafts` CLI.
  Default destination is Drafts; override to clipboard only when the user explicitly
  says "pbcopy", "clipboard", or "to clipboard". Drafts triggers: "copy it",
  "give it to me", "send it to me", "give me a draft", "send to drafts", "read it
  back", "what does it say", "pull from drafts", "get the draft", or /drafts.
  Primary method for delivering substantive content to the user.
---

# Drafts

Content exchange between Claude and the user via the `drafts` CLI on macOS.

## Write to Drafts (default)

Create a new draft, tagged so the user can filter Claude-generated content:

```bash
drafts create "CONTENT HERE" --tag claude
```

Confirm: "Sent to Drafts."

## Read from Drafts

Read the currently open draft on the user's Mac:

```bash
drafts current
```

If the user references a draft by description rather than what's open, search:

```bash
drafts --json search "QUERY"
```

If `drafts current` returns empty, ask the user to open the draft on their Mac.

## Iterating on a draft

When the user wants to refine an existing draft, capture the UUID from the read
and update in place rather than creating a new one:

```bash
drafts update <uuid> "REVISED CONTENT"
```

## Write to clipboard (explicit override only)

Only when the user explicitly says "pbcopy", "clipboard", or "to clipboard":

```bash
printf '%s' "CONTENT HERE" | pbcopy
```

Confirm: "Copied to clipboard."

## Behavior

- When the user asks to send/copy/give content, identify the most recent draft or
  content from the conversation and write it.
- When the user asks to read back or check edits, read from Drafts and display the content.
- During iterative editing sessions, read back automatically when the user indicates they made changes.
- Default to Drafts. Only use pbcopy when the user explicitly names "clipboard" or "pbcopy".
- Always tag Claude-created drafts with `claude`.
