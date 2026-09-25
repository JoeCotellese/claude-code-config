---
name: review
description: "Spaced repetition review of a parlo language deck using the smem CLI. Invoke with /parlo:review [code] [count] or when the user says 'quiz me', 'study time', 'flash cards', or 'review cards'."
effort: low
---

# parlo review

Runs an interactive spaced repetition session with the `smem` CLI. The deck
comes from the language profile, so there's no guessing which one.

## smem basics

`smem` stores flashcards in decks with SM-2 scheduling. Every command prints
JSON: `{"status": "ok", "data": {...}}` or
`{"status": "error", "message": "...", "code": "..."}`.

```bash
smem review next --deck <id> [--count <n>]   # due cards
smem review answer <card-id> --quality <0-5> # record a rating
smem review stats --deck <id>                # deck progress
```

## Start

```bash
P=$(${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh profile [code])
```

If that fails, relay its message. Read `smem_deck_id` from the profile. If
it's null, tell the user to run `/parlo:setup` to build the deck.

Run `smem review stats --deck <id>` and report how many cards are due. Use
the profile's `style` and `level` for how much of the language to use in
session chatter. When the profile's `show_pronunciation` is true, put simple phonetics
(stressed syllable in caps, not IPA) under every target-language phrase you show.

## Card loop

Fetch one card at a time with `smem review next --deck <id>`.

1. Show only the `front`, which is English. The user answers in the target
   language, out loud first if they can.
2. Reveal the `back` and play it with
   `${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh say "$P" "<back>"`. If their answer differs, say what differed and why in
   one line. Close counts as close; don't praise. A missing accent is a note, not a wrong answer, unless the accent changes the meaning (a word that means something else without it); then it counts as wrong. The user may type an apostrophe after a vowel in place of an accent.
3. Ask for a self-rating. Show the full scale on the first card only:

   ```
   0 = blank    3 = hard but correct
   1 = wrong    4 = good
   2 = close    5 = instant
   ```

4. Record it with `smem review answer <card-id> --quality <n>`.

Continue until no cards are due, the count argument is reached, or the user
says stop (in English or the target language).

## End

Run the stats command again. Report cards reviewed, how many were hard
(rated 0-2), and when the next cards come due.

## Edge cases

- **No due cards:** report the next due date from the stats. Suggest
  `/parlo:drill` instead.
- **Empty deck:** tell the user to run `/parlo:setup` to build cards.
- **smem not installed:** "smem CLI not found. Install it:
  `cd ~/git/spacedmemory && uv tool install -e .`"
