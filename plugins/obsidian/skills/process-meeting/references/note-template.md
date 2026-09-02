# Meeting Note Template

## Frontmatter

```yaml
---
tags:
  - type/meeting
  - <domain-tags>
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
participants:
  - "[[Full Name]]"
source: "Google Meet - Gemini Notes"
---
```

## Body Structure

```markdown
# <Participant A> <> <Participant B> - YYYY-MM-DD

## Topic: <Title>
*Timestamp: HH:MM:SS - HH:MM:SS*

<Narrative summary capturing what was discussed, why it matters, and the situational
context. Write as coherent paragraphs, not bullet points. Include the reasoning, stories,
analogies, and evidence that led to decisions. This is the primary value — Gemini captures
the what, we capture the why.>

**Decisions:**
- <specific decision, stated clearly>

**Open Questions:**
- <unresolved item>

---

## Topic: <Next Title>
*Timestamp: HH:MM:SS - HH:MM:SS*

<...repeat pattern...>

---

## Action Items

- [ ] **<Owner>**: <actionable task description>
- [ ] **<Owner>**: <actionable task description>

---

## Suggested Permanent Notes

- **<Topic>** — <one-line rationale for why this deserves an evergreen note>

---

## Questions

- <open questions or areas for further exploration>

## References

- Source transcript: Google Meet recording, YYYY-MM-DD HH:MM TZ
- [[Related Note]] - <brief context for why it's related>
```

## Guidelines

- **Narrative quality**: Each topic summary should be good enough that someone who wasn't in the meeting understands not just what was decided, but why. Include the stories and analogies that shaped the decision.
- **Decisions must be scannable**: Even though narratives flow as paragraphs, decisions get their own bulleted list for quick reference.
- **Action items are standalone**: Each should make sense without reading the full note.
- **Wiki-links**: Use `[[Note Title]]` for any concept that has or should have its own note.
- **Obsidian URLs**: When referencing this note externally (Todoist, calendar), use: `obsidian://open?vault=obsidian-vault&file=6_Meetings%2F<url-encoded-filename>.md`
