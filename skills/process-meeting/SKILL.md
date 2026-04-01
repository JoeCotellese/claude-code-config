---
name: process-meeting
description: >
  Process Google Meet transcripts from Google Drive into structured Obsidian vault meeting notes
  with topic extraction, vault linking, Todoist action items, and calendar deadlines. Invoke with
  `/process-meeting`, `/process-meeting latest`, or `/process-meeting YYYY-MM-DD`. Also trigger
  when user says "process meetings", "pull in transcripts", "process today's meeting", or asks
  to import meeting notes from Google Drive.
---

# Process Meeting

Transform Google Meet recordings (Gemini notes with embedded transcripts) into structured
Obsidian vault notes. Extracts topics with what/why/context narratives, links to existing
vault knowledge, creates Todoist action items, and adds calendar deadlines.

## Pipeline

Run stages sequentially. Each stage is a checkpoint — if a later stage fails, earlier work is preserved.

```
Fetch → Parse → Write → Link → Action → Calendar
```

**Time awareness:** Before starting, check the current date and time (run `date`). Sessions can span date boundaries — do not rely on the date provided at session start. Use the freshly checked date for all references to "today", relative dates, and temporal language in output.

## Stage 1: Fetch

**Configured sources:** Read from `config.json` in this skill's directory. Each source has a `name`, `remote` (rclone path), and `flags` array. See `config.example.json` for the schema.

Iterate over all sources from config. For each, list and pull files as plain text:
```bash
rclone copy --drive-export-formats txt "<remote>" /tmp/meet-staging/ --include "<filter>" [flags]
```

Filter files to only those containing "Notes by" (Gemini meeting notes with embedded transcripts).

**Argument handling:**
- No argument: default to `today` (current date only)
- `all`: process all unprocessed meetings from all sources (warn user about volume first)
- `latest`: most recent file only (across all sources)
- `today`: resolve to current date, then match
- `YYYY-MM-DD`: files matching that date
- `week`: last 7 days
- `month`: last 30 days

**When no argument is provided and no meetings are found for today**, ask the user: "No meetings found for today. How far back should I look?" and offer options: `latest`, `week`, `month`, or a specific date.

**Deduplication:** Scan `2_Literature Notes/` for existing meeting notes. Match by date AND participant names to avoid collisions (multiple meetings on the same day across sources). Skip any meeting that already has a corresponding note.

**Important:** Fullwidth slashes (`／`) in Google Drive filenames break `rclone cat`. Always use `rclone copy` with `--include` glob patterns.

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
