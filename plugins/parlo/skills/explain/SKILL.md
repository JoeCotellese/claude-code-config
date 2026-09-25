---
name: explain
description: "Break down foreign-language phrases from recent conversation, or a phrase given as an argument, using the active parlo profile. Invoke with /parlo:explain [phrase] or when the user says 'what did you say?', 'explain that', 'break that down', or says they don't understand in the language they're learning."
effort: low
---

# parlo explain

A quick reference for phrases in the language being learned. It isn't a
lesson.

## Load

```bash
P=$(${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh profile [code])
```

If there are several profiles and no code, pick the one matching the phrase's
language. Use `language`, `forvo`, and `level` from the profile. With no
profile at all, still explain the phrase, and mention `/parlo:setup` once.

## What to break down

- If an argument was given, break down that phrase.
- Otherwise, scan the last 5-10 messages for phrases in the target language.
- If there are none, say so in one line and ask which phrase they mean.

## Format

For each phrase (group related ones together):

**[phrase]**
- Meaning: [English]
- Literally: [word-for-word], only for idioms where it differs from the meaning
- Say it: [simple phonetics, stressed syllable in caps, not IPA]
- Hear it: play the phrase with
  `${CLAUDE_PLUGIN_ROOT}/scripts/parlo.sh say "$P" "<phrase>"`. If that fails
  for lack of `config.json`, link Forvo instead:
  `https://forvo.com/word/<key word>/#<forvo>`
- Note: [one line of grammar], only when it explains the meaning

Keep single words to Meaning, Say it, and Hear it. Play one phrase at a time
so the user can tell which audio is which.

## Corrections

If the user attempted the language and got something wrong, say what they
wrote, what it should be, and why, in one line. Skip scripted praise.

## Close

End with one related phrase they could use next. If a phrase was new to
them, offer to add it to their deck with English on the front:

```bash
smem card add --deck <smem_deck_id> --front "<english>" --back "<phrase>"
```
