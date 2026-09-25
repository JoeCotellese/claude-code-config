---
name: setup
description: "Build or extend a parlo language profile: 8-10 core sentences, word swaps, the essentials, and an smem deck. Invoke with /parlo:setup <language> or when the user says 'start learning <language>', 'set up <language>', 'add core sentences', or 'rebuild my deck'."
---

# parlo setup

Builds the smallest set of material that gets someone speaking: 8-10 core
sentences they can remix, plus a one-page reference. The output is a profile
at `~/.config/parlo/<code>.json` and an smem deck made from it. Every other
parlo skill reads that profile, so nothing about the language lives in a skill.

Helper: `${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh` (`profile`, `check`, `cards`).
Schema and a filled-in sample: `${CLAUDE_PLUGIN_ROOT}/profile.example.json`.

Keep the session moving. The method's warning is that collecting material
replaces speaking; aim to finish in one sitting and get the user saying
sentences out loud before it ends.

## 0. Start

Map the argument to an ISO 639-1 code (`es`, `ja`, `pt`). If
`parlo.sh profile <code>` finds a profile, load it and ask what to change
(add sentences, add swaps, update level, rebuild cards) instead of starting
over. Otherwise ask, one at a time:

- Why they're learning it. This steers which sentences are worth having.
- Current level.
- Which languages they already know.
- How they want Claude to use the language in conversation (goes in `style`).
- Whether to show phonetics under every phrase until they learn the sounds
  (`show_pronunciation`, default true for beginners). While it's true, show
  phonetics under every phrase in this setup too.

## 1. Difficulty scan

Answer these four in one line each, for this learner (fills `difficulty`):

- Word order compared with languages they know.
- Noun cases, if any.
- Sounds that will be new.
- Closest language they already know.

These are Tim Ferriss's questions for sizing up a language.

## 2. Core sentences

Propose 8-10 sentences drawn from the learner's reason for learning. Across
the set, cover:

- present, past, future, and a conditional or polite request
- I, you, we, and a third person
- formal and informal "you" if the language has both
- one question word, one yes/no question, one negative

For each sentence, show the target text, English, and its parts (subject,
verb, object), plus one swap: the same pattern with one slot changed. Let the
user edit the list before saving. Prefer sentences they'd say in their real
life over textbook sentences.

## 3. Essentials

Answer the four questions briefly. This is a reference card, not a grammar
book:

- `common`: 8-15 of the most common words and phrases, each with a
  `target`/`english` pair.
- `verbs`: present tense of the 3-6 most useful verbs.
- `questions_negatives`: how questions and negatives form, in one or two
  sentences.
- `patterns`: 3-5 key grammar patterns, one line each.

## 4. Save and validate

```bash
mkdir -p ~/.config/parlo
# write the profile, then:
${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh check ~/.config/parlo/<code>.json
```

Fix whatever `check` names and re-run it until it prints `ok`.

## 5. Build the deck

If `smem_deck_id` is null, run `smem deck list`. Offer an existing deck for
this language if there is one, otherwise create one:

```bash
smem deck create --name "<language>" --description "parlo core sentences"
```

Write the id into the profile. Then generate cards, skipping any front the
deck already has, and import them:

```bash
smem io export --deck <id> > <scratch>/existing.json
${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh cards <profile> <scratch>/existing.json > <scratch>/cards.json
smem io import --deck <id> --file <scratch>/cards.json
```

The cards go English to target language, so review drills producing the
language, not recognizing it.

## 6. First reps

For each core sentence, play it with
`${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh say <profile> "<target>"`, then have
the user say it out loud. Show the target text, its phonetics when
`show_pronunciation` is true, and its English, so the sounds attach to a
meaning. Audio is generated once through ElevenLabs and
reused from `~/.config/parlo/audio/` after that.

If `say` reports a missing `~/.config/parlo/config.json`, offer to create it
from `${CLAUDE_PLUGIN_ROOT}/config.example.json`. Store the API key as an
`op://` reference, never the raw key. A profile may set its own `voice_id` to
override the default voice with a native speaker for that language.

Then point them to:

- `/parlo:drill`: daily speaking practice with word swaps.
- `/parlo:review`: spaced repetition through smem.
- `/parlo:explain`: breaks down anything in the language they don't follow.

If their CLAUDE.md doesn't mention the profile yet, suggest adding one line
naming it so every session knows the active language.
