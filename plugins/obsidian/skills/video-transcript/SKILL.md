---
name: video-transcript
description: Pull a YouTube video's transcript into context for discussion — no notes written. Invoke with `/video-transcript <youtube-url>` or when user says "pull the transcript", "transcript this video", "let me read this video first", "what does this video say". Downloads and cleans the transcript via yt-dlp, then summarizes it for conversation. Hand off to `/video-to-zettelkasten` when ready to make notes.
---

# Video Transcript

Fetch a YouTube video's transcript, clean it, load it into context, and discuss
it. This skill stops at "here's what the video says" — it writes no notes. When
the user is ready to turn the conversation into permanent notes, hand off to
`/video-to-zettelkasten`, which reuses the same cleaned transcript already on
disk.

## Workflow

1. **Download metadata** — keep only the useful fields:
   ```bash
   yt-dlp --dump-json --no-download "<url>" | jq '{title, uploader, channel, upload_date, duration, webpage_url, id, description: (.description | .[0:500])}'
   ```

2. **Download transcript** — manual and auto subs in one call:
   ```bash
   yt-dlp --write-subs --write-auto-subs --sub-langs "en" --skip-download --sub-format vtt -o "/tmp/yt-zk-%(id)s" "<url>"
   ```
   Note the `yt-zk-` prefix and `/tmp` path are shared with `video-to-zettelkasten` on purpose — that skill looks for exactly this file to skip its own fetch.

3. **Clean the transcript** — reuse the bundled script from the ZK skill:
   ```bash
   python3 /Users/joec/.claude/skills/video-to-zettelkasten/scripts/clean-vtt.py /tmp/yt-zk-<id>.en.vtt
   ```
   This writes a cleaned `.txt` next to the `.vtt` and prints the word count. Then **use the Read tool** on the cleaned `.txt` — do not pipe it through `cat`/`sed`/`head`.

4. **Summarize for discussion** — present:
   - Video title, channel, duration, upload date
   - A 3-5 sentence summary of what the transcript covers and its main argument
   - 3-6 bullet points of the most notable ideas, claims, or moments

   Then stop and let the user drive the conversation. Answer questions against
   the transcript already in context. Do **not** write any files.

## Handoff to notes

When the user says "ZK this", "make notes", "atomize it", or similar, invoke
`/video-to-zettelkasten <url>`. The cleaned `/tmp/yt-zk-<id>.en.txt` is already
on disk, so that skill skips its own fetch and goes straight to extraction.

Leave `/tmp/yt-zk-*` in place until the notes are written — that's the handoff
artifact. Only clean up if the user ends without making notes.

## Example Invocations

- `/video-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- "Pull the transcript for https://youtu.be/abc123, I want to read it first"
- "What does this talk actually say?" (with URL in message)
