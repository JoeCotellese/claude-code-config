---
name: process-meeting
effort: medium
description: >
  Process Google Meet transcripts from Google Drive OR Apple Voice Memos into structured
  Obsidian vault notes with topic extraction, vault linking, Todoist action items, and
  calendar deadlines. Invoke with `/process-meeting`, `/process-meeting latest`,
  `/process-meeting YYYY-MM-DD`, or `/process-meeting voice [latest|today|YYYY-MM-DD]`
  for Apple Voice Memo recordings transcribed locally via mlx-whisper. Also trigger when
  user says "process meetings", "pull in transcripts", "process today's meeting", "process
  voice memo", "transcribe my memo", or asks to import meeting notes from Google Drive or
  voice memos.
---

# Process Meeting

Transform Google Meet recordings (Gemini notes with embedded transcripts) OR Apple Voice
Memo recordings (transcribed locally via mlx-whisper) into structured Obsidian vault notes.
Extracts topics with what/why/context narratives, links to existing vault knowledge, creates
Todoist action items, and adds calendar deadlines.

## Source modes

Two pipelines, picked by subcommand:

- **Default (Google Meet)**: pulls Gemini notes from Google Drive via rclone. See [Google Meet Pipeline](#google-meet-pipeline) below.
- **`voice` subcommand (Apple Voice Memos)**: reads .m4a files from the iCloud-synced Voice Memos folder, transcribes with mlx-whisper, then routes to a solo or multi-person template. See [Voice Memo Pipeline](#voice-memo-pipeline) below.

## Google Meet Pipeline

Run stages sequentially. Each stage is a checkpoint — if a later stage fails, earlier work is preserved.

```
Fetch → Parse → Write → Link → Action → Calendar
```

**Time awareness:** Before starting, check the current date and time (run `date`). Sessions can span date boundaries — do not rely on the date provided at session start. Use the freshly checked date for all references to "today", relative dates, and temporal language in output.

## Stage 1: Fetch

**Configured sources:** Read from `config.json` in this skill's directory. Each source has a `name`, `remote` (rclone path), and `flags` array. See `config.example.json` for the schema.

Iterate over all sources from config. First list files with `rclone lsf`, then copy matches as plain text.

**CRITICAL — Date format in filenames:** Google Drive filenames use fullwidth slashes (`／`, Unicode U+FF0F) as date separators, NOT regular slashes or hyphens. A file dated April 2, 2026 appears as `2026／04／02` in the filename. You MUST use fullwidth slashes in all `--include` patterns and grep filters. Standard hyphens (`-`) or regular slashes (`/`) will silently match nothing.

To list files for a given date:
```bash
rclone lsf "<remote>" [flags] | grep "2026／04／02"
```

To fetch files for a given date:
```bash
rclone copy --drive-export-formats txt "<remote>" /tmp/meet-staging/ --include "*2026／04／02*" [flags]
```

Filter files to only those containing "Notes by" (Gemini meeting notes with embedded transcripts).

**Argument handling:**
- No argument: default to `today` (current date only)
- `all`: process all unprocessed meetings from all sources (warn user about volume first)
- `latest`: most recent file only (across all sources)
- `today`: resolve to current date, then use fullwidth slash format `YYYY／MM／DD` for matching
- `YYYY-MM-DD`: convert to fullwidth slash format `YYYY／MM／DD` for matching
- `week`: last 7 days
- `month`: last 30 days

**When no argument is provided and no meetings are found for today**, ask the user: "No meetings found for today. How far back should I look?" and offer options: `latest`, `week`, `month`, or a specific date.

**Deduplication:** Scan `2_Literature Notes/` for existing meeting notes. Match by date AND participant names to avoid collisions (multiple meetings on the same day across sources). Skip any meeting that already has a corresponding note.

**Important:** Fullwidth slashes (`／`) in Google Drive filenames break `rclone cat`. Always use `rclone copy` with `--include` glob patterns, never `rclone cat` with fullwidth-slash filenames.

## Stage 2: Parse

Use the **full transcript** (everything after the `Transcript` marker), NOT Gemini's summary. The transcript is the source of truth — it captures the reasoning and context that Gemini loses.

For each meeting:

1. **Identify distinct topics** from conversation flow and timestamp markers (`00:09:56` format). A new topic = substantive subject shift.

2. **For each topic extract:**
   - Title (concise, descriptive)
   - Timestamp range
   - Narrative summary: what was discussed, why it matters, situational context — as a **coherent paragraph**, not a form. Capture reasoning, stories, analogies, and evidence behind decisions.
   - Decisions made (bulleted)
   - Open questions (bulleted)

3. **Extract action items** with owners and due dates if mentioned

4. **Extract hard deadlines** — conferences, launches, external commitments with dates

**Participant names:** Parse from transcript speaker labels (e.g., `Jonah Harris:`, `Joe Cotellese:`).

## Stage 3: Write

Create note at: `2_Literature Notes/YYYYMMDD - <Participants> Meeting - <Brief Description>.md`

See [references/note-template.md](references/note-template.md) for the complete template.

Key rules:
- Brief description: derive from 2-3 most significant topics, under 60 characters
- Domain tags: infer from content. Common: `nextgres`, `business`, `engineering`, `productmanagement`, `ai`, `database`
- Participants as `[[wiki-links]]` in frontmatter

## Stage 4: Link

After writing the note:

1. **Search vault** (`3_Permanent Notes/`, `2_Literature Notes/`, `4_Projects/`) for concepts mentioned in the meeting
2. **Add `[[wiki-links]]`** inline where matches exist
3. **Add "Suggested Permanent Notes" section** at the end — topics that might deserve their own evergreen note in `3_Permanent Notes/`. One-line rationale each. Do NOT auto-create.

## Stage 5: Action Items → Todoist

**Only consider tasks owned by the vault owner (Joe Cotellese).** Other participants' action items should appear in the meeting note but NOT be pushed to Todoist.

1. **Present proposed tasks** using `AskUserQuestion` with `multiSelect: true`. Each option should be:
   - **label**: The task title (concise, actionable)
   - **description**: Standalone context so the user can judge whether it's a real action item

2. **Create only selected tasks** via Todoist MCP `add-tasks`. If the user selects none, skip task creation entirely.

3. **If no Joe action items were extracted**, skip this stage entirely — do not prompt.

For each selected task:
- **content**: Clear, actionable task title
- **description**: Standalone context + Obsidian link: `obsidian://open?vault=obsidian-vault&file=2_Literature%20Notes%2F<filename>.md`
- **dueString**: From transcript context if date/timeframe mentioned, otherwise omit
- Destination: **inbox** (no projectId)

## Stage 6: Calendar (iMCP)

Only for **hard deadlines** — conferences, launches, contractual dates.

- Create calendar event via iMCP MCP tools
- Add notice period scaled to urgency (1 week for month-out, 2-3 days for week-out)
- **If iMCP not connected:** Warn user with list of deadlines needing manual entry. Do NOT fail.

## Completion Output

```
## Meeting Processing Complete

**Processed:** <count> meeting(s)
**Notes created:**
- [Title](obsidian://open?vault=...) — <topic count> topics

**Todoist tasks created:** <count>
**Calendar events:** <count> (or "iMCP offline — <count> deadlines need manual entry")

**Suggested Permanent Notes:**
- <topic> — <rationale>
```

---

## Voice Memo Pipeline

Triggered by `/process-meeting voice [latest|today|YYYY-MM-DD]`. Two paths inside this pipeline: solo (notes-to-self) and multi-person (recorded conversation). See [references/voice-memo-template.md](references/voice-memo-template.md) for the templates and classification heuristic.

```
Fetch → Transcribe → Classify → Parse → Write → Link → Action → Calendar
```

### Stage 1: Fetch

**Source folder:** `~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/`

**Filename format:** `YYYYMMDD HHMMSS[-HEXID].m4a` (Apple-assigned). User-renamed memos may use arbitrary names — accept both. Date is parsed from the leading `YYYYMMDD` token when present; otherwise fall back to the file's `mtime`.

List recordings:
```bash
ls "$HOME/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/"*.m4a
```

**Argument handling:**
- `voice` (no further arg): default to `today`
- `voice latest`: most recent .m4a by mtime
- `voice today`: today's date in `YYYYMMDD` prefix match
- `voice YYYY-MM-DD`: specific date — convert to `YYYYMMDD` prefix match
- `voice all`: all unprocessed (warn about volume first)

**Deduplication:** Scan `1_inbox/` (solo path) and `2_Literature Notes/` (multi-person path) for any note whose frontmatter `source_file` matches the .m4a basename. Skip already-processed.

### Stage 2: Transcribe

Run mlx-whisper via the helper script:

```bash
~/.claude/skills/process-meeting/scripts/transcribe-voice.sh \
  "<input.m4a>" \
  /tmp/voice-staging/
```

The script outputs `/tmp/voice-staging/<basename>.txt`. Default model is `mlx-community/whisper-large-v3-mlx` (override via `MLX_WHISPER_MODEL` env var). The script exits with code 69 if `mlx_whisper` is not on PATH — install with `uv tool install mlx-whisper`.

**Long recordings:** Run transcription in the background (`run_in_background: true`) for files >5 minutes; the model takes roughly real-time on Apple Silicon. Don't poll — wait for completion notification.

### Stage 3: Classify

Apply the heuristic in [references/voice-memo-template.md](references/voice-memo-template.md):

- Single first-person narrator throughout → **solo path**
- Question/answer turns or proper-name addressing ("Hey Jonah") → **multi-person path**
- Ambiguous / short (<60s) → default solo, but ask if uncertain

When uncertain, ask the user with `AskUserQuestion` showing a 2-3 sentence transcript excerpt for context.

### Stage 4: Parse

**Solo path:**
- Identify the through-line (the dominant subject the user is thinking about)
- Extract: 2-4 sentence summary, key thoughts (bullets), decisions, action items, open questions
- Title: under 60 characters, derived from the dominant subject

**Multi-person path:**
- Same as Google Meet Stage 2 (topics + narrative + decisions + open questions + action items)
- Speaker attribution: mlx-whisper does NOT diarize. Infer participants from name mentions ("hey Jonah", "Joe asked"). If unclear, prompt user.
- Replace timestamp lines with `*Approx: <ordinal>*` (e.g., "Approx: opening third") or omit.

### Stage 5: Write

**Solo path:** `1_inbox/YYYYMMDDHHMMSS - Voice Memo - <Title>.md` — see solo template in [references/voice-memo-template.md](references/voice-memo-template.md). Tag includes `voice-memo`.

**Multi-person path:** `2_Literature Notes/YYYYMMDD - <Participants> Meeting - <Brief Description>.md` — same as Google Meet path but with `source: "Apple Voice Memo - mlx-whisper transcript"` and added `source_file`/`duration` frontmatter fields.

### Stage 6: Link

Same as Google Meet Stage 4 — search vault, add `[[wiki-links]]`, append "Suggested Permanent Notes" section. Solo memos may yield fewer links because they're more fleeting; that's fine.

### Stage 7: Action Items → Todoist

Same Joe-only rule as Google Meet Stage 5. Solo memos often surface latent todos ("I should call X") — capture those as actionable Todoist tasks with the Obsidian deep link in the description.

### Stage 8: Calendar (iMCP)

Same as Google Meet Stage 6. Voice memos rarely contain hard deadlines, but if one is dictated, treat identically.

### Voice Memo Completion Output

```
## Voice Memo Processing Complete

**Processed:** <count> recording(s)
**Path:** <solo|multi-person|mixed>
**Notes created:**
- [Title](obsidian://open?vault=...) — <path>

**Todoist tasks created:** <count>
**Calendar events:** <count>
```
