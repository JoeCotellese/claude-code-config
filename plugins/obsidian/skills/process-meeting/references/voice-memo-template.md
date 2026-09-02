# Voice Memo Templates

Two paths, classified before write. Solo = notes-to-self captured solo. Multi-person = recorded conversation with two or more voices.

## Solo Path — destination `1_inbox/`

Filename: `YYYYMMDDHHMMSS - Voice Memo - <Title>.md` (timestamp from voice memo filename, title derived from content).

```markdown
---
tags:
  - type/note
  - voice-memo
  - <domain-tags>
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
source: "Apple Voice Memo - mlx-whisper transcript"
source_file: "<original .m4a basename>"
duration: "<MM:SS>"
---

# <Title>

## Summary

<2-4 sentence narrative paragraph capturing the gist. Not a topic-by-topic breakdown — voice
memos to self are usually one stream of thought, even if it meanders.>

## Key Thoughts

- <bulleted, concise distillation of the substantive points>

## Decisions

- <decision made, stated as a fact (skip section if none)>

## Action Items

- [ ] **Joe**: <actionable task — same Joe-only rule as meeting notes>

## Open Questions

- <unresolved threads to revisit (skip if none)>

## References

- Source recording: `<original .m4a basename>`
- Recorded: YYYY-MM-DD HH:MM
- [[Related Note]] - <brief context>
```

### Solo guidelines

- **Title**: derive from dominant subject — under 60 characters, descriptive not clever.
- **Summary first, bullets second**: voice memos ramble. Capture the through-line as prose, then strip it to bullets in Key Thoughts.
- **No timestamps in body**: voice memos rarely have meaningful time markers. Skip the Topic-with-timestamp structure entirely.
- **Tag `voice-memo`** so all voice-captured fleeting notes can be filtered as a cohort.

## Multi-Person Path — destination `6_Meetings/`

Use the standard meeting note template at [note-template.md](note-template.md). Adjustments:

- **No speaker diarization**: mlx-whisper produces flat text without speaker labels. Infer participants from content (names mentioned, "I told X", etc.) and prompt user if unclear.
- **No reliable timestamps**: replace `*Timestamp: HH:MM:SS - HH:MM:SS*` with `*Approx: <ordinal>*` (e.g., "Approx: opening third") or omit the timestamp line entirely.
- **Source field**: `source: "Apple Voice Memo - mlx-whisper transcript"` instead of `"Google Meet - Gemini Notes"`.
- **Add `source_file` and `duration`** to frontmatter for traceability back to the original .m4a.

## Classification heuristic

Before writing, check the transcript:

- **Single first-person narrator throughout** ("I want to...", "I'm thinking about...", no second-person dialogue) → solo path.
- **Question/answer turns or proper-name addressing** ("Hey Jonah", "what do you think") → multi-person path.
- **Ambiguous / short (<60s)** → default to solo unless user says otherwise.

When in doubt, ask the user before committing to a path.
