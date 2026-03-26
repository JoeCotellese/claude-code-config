---
name: video-to-zettelkasten
description: Decompose YouTube videos into atomic Zettelkasten permanent notes in the Obsidian vault. Invoke with `/video-to-zettelkasten <youtube-url>` or when user says "ZK this video", "atomize this video", "extract notes from this video". Downloads transcript via yt-dlp, extracts concepts, and creates interlinked permanent notes plus a literature note.
---

# Video to Zettelkasten

Decompose a YouTube video's transcript into atomic, interlinked permanent notes following Zettelkasten methodology. Uses `yt-dlp` to fetch the transcript and video metadata, then produces permanent notes in `3_Permanent Notes/` plus a literature note in `2_Literature Notes/`.

Read [references/vault-standards.md](references/vault-standards.md) for Obsidian vault formatting standards before creating any notes.

## Workflow

### Phase 1: Fetch Transcript and Metadata

1. **Download metadata** — Run:
   ```bash
   yt-dlp --dump-json --no-download "<url>"
   ```
   Extract: `title`, `uploader` (channel name), `upload_date`, `duration`, `description`, `webpage_url`, `id`

2. **Download transcript** — Try manual subtitles first, fall back to auto-generated:
   ```bash
   # Try manual English subs first
   yt-dlp --write-subs --sub-langs "en" --skip-download --sub-format vtt -o "/tmp/yt-zk-%(id)s" "<url>"
   ```
   If no manual subs found:
   ```bash
   # Fall back to auto-generated subs
   yt-dlp --write-auto-subs --sub-langs "en" --skip-download --sub-format vtt -o "/tmp/yt-zk-%(id)s" "<url>"
   ```

3. **Read and clean the transcript** — Read the `.vtt` file from `/tmp/` and clean it:
   - Strip VTT headers and timestamp lines
   - Remove duplicate consecutive lines (auto-subs repeat fragments)
   - Merge sentence fragments across line breaks
   - Add punctuation where clearly missing (end-of-sentence detection)
   - Collapse excessive whitespace
   - Present the cleaned transcript length to the user (e.g., "~3,200 words")

4. **Check for existing notes** — Search the vault:
   - `Grep` for the video title across `**/*.md`
   - `Glob` for filename matches in `2_Literature Notes/` and `3_Permanent Notes/`

### Phase 2: Analyze and Propose Structure

Present video context to the user:
- Video title, channel, duration, upload date
- Brief summary of what the transcript covers (2-3 sentences)

Extract concepts at two tiers:

**Tier 1 - Core Concepts** (always extract)
- The video's central ideas, frameworks, or arguments
- Ideas that stand alone as reusable mental models
- Typically 2-4 notes per video

**Tier 2 - Supporting Ideas** (extract when the video has depth)
- Taxonomies, examples, or methods that enrich the core concepts
- Actionable procedures or decision frameworks
- Typically 1-3 notes per video

For long-form content (lectures, deep dives over 30 minutes), also consider:

**Tier 3 - Tactical Methods** (only for substantial videos)
- Step-by-step methods, checklists, or frameworks for action
- Typically 1-2 notes

**Present the proposed structure to the user before creating notes.** Show:
- Proposed note titles organized by tier
- One-line description of what each captures
- Estimated total note count

Wait for user approval before proceeding.

### Phase 3: Create Permanent Notes

For each approved note, write to `3_Permanent Notes/` following this structure:

```markdown
---
tags:
  - type/note
  - domain-tag-1
  - domain-tag-2
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
---

# [Concept Title]

[1-3 sentence definition/summary of the concept distilled to its essence]

## [Core content sections - vary by concept type]

[Use tables, blockquotes, lists as appropriate. Prefer tables for comparisons.
Use blockquotes for memorable quotes from the speaker.
Keep content dense but scannable.]

## Questions
- [Open questions connecting this concept to the reader's world]
- [Areas for further exploration]
- [How does this relate to other domains?]

## Terms
- [[Related Concept Note]]
- [[Another Related Note]]

## References
- [[videox - Video Title]] - Channel Name
- [Other sources if applicable]
```

**Content principles:**
- **Atomic**: One concept per note. If you're writing "and also..." it's probably two notes.
- **Evergreen**: Write as timeless knowledge, not "the speaker says at 14:32..."
- **Dense**: Use tables for structured comparisons. Use blockquotes for the speaker's best lines. No filler.
- **Interlinked**: Every note should link to 2-5 other notes from the same video. Use `[[wiki-links]]` for notes that exist and `[[Proposed Title]]` for ones being created in the same batch.
- **Aliased links**: Use `[[Full Title|Short Display]]` when the full title is unwieldy inline.
- **Questioning**: End with 2-4 genuine questions that connect the concept to the reader's domain or to other sources in the vault.

**What NOT to include:**
- Timestamps or "the speaker says" framing
- Exhaustive examples (pick 2-3 best ones)
- Content that merely recaps the video narrative without extracting a reusable idea

### Phase 4: Create Literature Note

Write to `2_Literature Notes/videox - [Title].md`:

```markdown
---
tags:
  - type/literature
  - video
  - youtube
  - domain-tag-1
  - domain-tag-2
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
source: "[video-url]"
channel: "[channel-name]"
duration: "[HH:MM:SS]"
upload_date: "[YYYY-MM-DD]"
---

# [Video Title]

**Channel:** [[Channel Name]]
**Duration:** X minutes
**URL:** [link]

## Summary
[3-5 sentence summary of the video's content and main argument]

## Core Concepts

### Tier 1
- [[Permanent Note Title]] — one-line description
- [[Another Note]] — one-line description

### Tier 2
- [[Supporting Note]] — one-line description

## Key Moments
[Chronological highlights from the transcript — not every section, just the most valuable points with brief context]

## Terms
- [[Permanent Note 1]]
- [[Permanent Note 2]]

## References
- Related works or sources mentioned in the video
```

**If updating existing literature note:** Add or update Core Concepts section, wiki-links, and Terms. Do NOT remove existing content.

### Phase 5: Verify Cross-Links

After all notes are created:
- Confirm every permanent note links back to the literature note
- Confirm every permanent note links to at least 2 sibling permanent notes
- Confirm the literature note's Core Concepts section lists all permanent notes by tier
- Search the vault for existing permanent notes on related topics and suggest cross-links to user

### Phase 6: Cleanup

Remove temporary files from `/tmp/`:
```bash
rm -f /tmp/yt-zk-*
```

## Example Invocations

- `/video-to-zettelkasten https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- "ZK this video https://youtu.be/abc123"
- "Extract notes from this talk" (with URL in message)
