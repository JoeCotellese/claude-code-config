---
name: learn
description: "Spaced repetition study session using smem CLI. Invoke with /learn or when user says 'quiz me', 'study time', 'flash cards', 'review cards'. Pulls due cards from smem and runs an interactive review."
effort: low
---

# Learn - Spaced Repetition Study Skill

Run an interactive spaced repetition session using the `smem` CLI tool.

## How smem Works

`smem` is a CLI tool that stores flashcards in decks with SM-2 scheduling. All output is JSON.

### Key Commands

```bash
# List all decks
smem deck list

# Fetch due cards (default 1, use --count for more)
smem review next --deck <deck-id> [--count <n>]

# Submit quality rating after review
smem review answer <card-id> --quality <0-5>

# Show deck progress
smem review stats --deck <deck-id>
```

### JSON Output Envelope

```json
{"status": "ok", "data": {...}}
{"status": "error", "message": "...", "code": "..."}
```

## Session Flow

### 1. Start

When invoked, first check what decks exist and which have due cards:

```bash
smem deck list
```

If multiple decks have due cards, ask which deck to study. If only one deck has due cards, use it. If a deck name or ID is provided as an argument, use that.

Then show deck stats:

```bash
smem review stats --deck <deck-id>
```

Report: "You have N cards due. Cominciamo?"

### 2. Card Loop

Fetch one card at a time:

```bash
smem review next --deck <deck-id>
```

Parse the JSON response. The card has `front` and `back` fields.

**Present the card:**
- Show only the `front` (the question)
- Hold back the `back` (the answer)
- Wait for the user's response

**After the user answers:**
- Reveal the `back` (correct answer)
- Compare their answer to the correct one — be encouraging, note if they were close
- Ask them to self-rate: "How'd you do? (0-5)"
  - 0 = complete blackout
  - 1 = wrong
  - 2 = wrong but recognized correct answer
  - 3 = correct with difficulty
  - 4 = correct with hesitation
  - 5 = instant recall

**Record the rating:**

```bash
smem review answer <card-id> --quality <rating>
```

**Then fetch the next card.** Continue until:
- No more cards are due (empty cards array in response)
- User says "stop", "done", "basta", or similar

### 3. End Session

When the session ends, show stats:

```bash
smem review stats --deck <deck-id>
```

Summarize: cards reviewed, how many were easy vs hard, when next cards are due.

End with an encouraging Italian phrase.

## Tone

- Conversational and encouraging
- Use Italian liberally (the user is learning)
- Correct mistakes gently with brief explanations
- Celebrate streaks and good recall
- Keep it moving — don't over-explain unless asked

## Arguments

- `/learn` — auto-detect deck with most due cards
- `/learn italian` — search for deck by name (case-insensitive partial match)
- `/learn 1` — use deck by ID
- `/learn 5` (with deck context) — review 5 cards then stop

## Quality Rating Guide

Show this on first card of each session, then abbreviate:

```
Rate yourself:
  0 = blank    3 = hard but correct
  1 = wrong    4 = good
  2 = close    5 = instant
```

## Edge Cases

- **No due cards:** "Niente da fare! No cards due. Next review: [date from next_due field]"
- **Empty deck:** "This deck has no cards. Add some with: smem card add --deck <id> --front '...' --back '...'"
- **smem not installed:** "smem CLI not found. Install it: cd ~/git/spacedmemory && uv tool install -e ."
