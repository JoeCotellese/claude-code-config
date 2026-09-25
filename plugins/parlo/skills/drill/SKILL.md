---
name: drill
description: "Daily speaking drill on the core sentences from a parlo profile: say it out loud, then swap words to build new sentences. Invoke with /parlo:drill [code] or when the user says 'drill me', 'practice speaking', 'daily reps', or 'sentence practice'."
---

# parlo drill

Step 4 of the method: say the core sentences out loud every day until they
feel natural, then remix them. Aim for 5-10 minutes.

## Load

```bash
P=$(${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh profile [code])
```

If that fails, relay its message (usually: run `/parlo:setup`). Read the
profile. Follow its `style` and `level` for how much of the language to use
around the drill itself. When the profile's `show_pronunciation` is true, put simple phonetics
(stressed syllable in caps, not IPA) under every target-language phrase you show.

## Round

Pick 3 or 4 sentences at random, at least one that isn't present tense. For
each one:

1. **Produce.** Show only the English. The user says it out loud, then types
   what they said.
2. **Check.** Show the target sentence and play it with
   `${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh say "$P" "<target>"` (generated on
   first use, then replayed from disk). Play at native speed; if the user asks
   for it slower, replay once with `PARLO_SPEED=0.75` and then go back to native.
   If they got it wrong, say what was
   wrong and why, in one line. Don't praise or cheerlead; a correct answer
   just moves on. A missing accent is a note, not a wrong answer, unless the accent changes the meaning (a word that means something else without it); then it counts as wrong. The user may type an apostrophe after a vowel in place of an accent.
3. **Swap.** Give a new English sentence using the same pattern with one slot
   changed (another subject, tense, or object), drawing on `essentials` for
   words. They produce it the same way.
4. **Invent.** Ask them to make their own swap. Correct it.

## Keep what works

When an invented swap comes out correct, or after a correction, offer to save
it. On yes, append it to that sentence's `swaps` in the profile, re-run
`parlo.sh check`, and add the card:

```bash
smem card add --deck <smem_deck_id> --front "<english>" --back "<target>"
```

## Close

Give one concrete prompt for using a sentence with a real person today.
Mistakes in real conversation are expected; early use matters more than
accuracy. If the user says the drill feels easy, suggest adding a sentence
with `/parlo:setup`.
