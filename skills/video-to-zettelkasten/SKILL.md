---
name: video-to-zettelkasten
effort: high
description: Decompose YouTube videos into atomic Zettelkasten permanent notes in the Obsidian vault. Invoke with `/video-to-zettelkasten <youtube-url>` or when user says "ZK this video", "atomize this video", "extract notes from this video". Downloads transcript via yt-dlp, fact-checks empirical claims against primary sources (with a cui bono check) before writing, extracts concepts, and creates interlinked permanent notes plus a literature note.
---

# Video to Zettelkasten

Decompose a YouTube video's transcript into atomic, interlinked permanent notes following Zettelkasten methodology. Uses `yt-dlp` to fetch the transcript and video metadata, then produces permanent notes in `3_Permanent Notes/` plus a literature note in `2_Literature Notes/`.

Read [references/vault-standards.md](references/vault-standards.md) for Obsidian vault formatting standards before creating any notes.

## Workflow

### Phase 1: Fetch Transcript and Metadata

**Skip if already fetched:** If a cleaned `/tmp/yt-zk-<id>.en.txt` already exists for this video (e.g. the user came from `/video-transcript`), Read it and the metadata you already have, then jump to Phase 2. Only run the steps below when no transcript is on disk.

1. **Download metadata** — Pipe through `jq` to keep only what you need (the raw JSON includes ~1MB of format/storyboard noise):
   ```bash
   yt-dlp --dump-json --no-download "<url>" | jq '{title, uploader, channel, upload_date, duration, webpage_url, id, description: (.description | .[0:500])}'
   ```

2. **Download transcript** — Fetch manual and auto-generated subs in one call; yt-dlp writes whichever exist:
   ```bash
   yt-dlp --write-subs --write-auto-subs --sub-langs "en" --skip-download --sub-format vtt -o "/tmp/yt-zk-%(id)s" "<url>"
   ```
   Most channels (especially tech/educational) only have auto-subs. Manual subs are rare.

3. **Clean the transcript with the bundled script** — Run:
   ```bash
   python3 /Users/joec/.claude/skills/video-to-zettelkasten/scripts/clean-vtt.py /tmp/yt-zk-<id>.en.vtt
   ```
   This writes a cleaned `.txt` next to the `.vtt` and prints the word count. Then **use the Read tool** on the cleaned `.txt` file — do not pipe it through `cat`/`sed`/`head`.

4. **Check for existing notes** — Search the vault:
   - `Grep` for the video title across `**/*.md`
   - `Glob` for filename matches in `2_Literature Notes/` and `3_Permanent Notes/`

### Phase 2: Verify Claims (conditional)

**When to run:** The video makes empirical claims — health, medical, nutrition, financial, scientific, or any "studies show / research proves" cause-and-effect assertion. Skip for pure opinion, tutorial, history, or commentary with nothing checkable. When unsure, run it.

Two independent checks:

1. **Evidence check.** For each substantive claim, find the primary source and judge whether it says what the video says. Delegate to parallel research agents (one per cluster of claims) with web access; have each return, per claim:
   - Verdict: SUPPORTED / OVERSIMPLIFIED / MISLEADING / UNSUPPORTED
   - The actual finding: real effect size, study design, population, sample size
   - Citation: authors, journal, year, URL
   - How the video distorted it, if it did

   Watch for the recurring failure modes: a fabricated or misattributed citation; a lab/surrogate marker (insulin, blood viscosity, a few mmHg of blood pressure, HRV) sold as a hard outcome (stroke, heart attack) the study never measured; an observational association stated as causation; a small or non-generalizable sample generalized to everyone; a real number inflated.

2. **Cui bono.** Determine who profits if the viewer believes the claims. The description is the primary source, and Phase 1's metadata pull truncates it to 500 chars — so fetch it in full and scan for the money trail:
   ```bash
   yt-dlp --dump-json --no-download "<url>" | jq -r '.description' \
     | rg -i 'https?://|discount|promo|code|amazon|lvnta|linktr|patreon|sponsor|waitlist|supplement|shop|store|join|free '
   ```
   Look across the full description, the channel (its "About" links, shop, membership), the transcript (a spoken sponsor read or "link below / use my code"), and optionally the pinned comment for: affiliate or storefront links, discount codes, supplement or product sales, a paid course or community, a waitlist or email capture, sponsorships, or a book. A creator selling the thing their claims make you want to buy is a conflict of interest that colors the whole video. State it plainly, naming what they're selling.

**Present the verdict before proposing notes** — a claim-by-claim scorecard plus the cui bono finding. Then let it steer Phase 3:
- Claims hold up → proceed normally.
- Claims are mixed or weak → build notes only around what survives, properly caveated, and reframe the literature note as an annotated debunk (claim → verdict → real finding + citation). Do NOT launder unverified claims into permanent notes as if they were knowledge.
- Consider a standalone permanent note for any reusable *reasoning* pattern the check exposes (e.g. the surrogate-endpoint-to-hard-outcome leap) — often more valuable than the video's content itself.

Ask the user how to proceed when the picture is mixed.

### Phase 3: Analyze and Propose Structure

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

**Auto-mode exception:** If auto mode is active (a `## Auto Mode Active` system reminder is present), skip the approval gate. Present the proposed structure inline and proceed with the writes in the same turn.

### Phase 4: Create Permanent Notes

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

### Phase 5: Create Literature Note

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

## Claim Check
[Include only when Phase 2 ran. A claim-by-claim scorecard with verdict and the
real finding + citation, plus the cui bono note (who profits). Omit this section
entirely for videos with nothing empirical to check.]

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

### Phase 6: Verify Cross-Links

After all notes are created:
- Confirm every permanent note links back to the literature note
- Confirm every permanent note links to at least 2 sibling permanent notes
- Confirm the literature note's Core Concepts section lists all permanent notes by tier
- Search the vault for existing permanent notes on related topics and suggest cross-links to user

### Phase 7: Cleanup

Remove temporary files from `/tmp/`:
```bash
rm -f /tmp/yt-zk-*
```

## Example Invocations

- `/video-to-zettelkasten https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- "ZK this video https://youtu.be/abc123"
- "Extract notes from this talk" (with URL in message)
