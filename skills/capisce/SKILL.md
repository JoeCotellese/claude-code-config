---
name: capisce
description: "Break down Italian phrases from recent conversation. Invoke with /capisce or when user asks 'what did you say?', 'explain the Italian', 'non capisco', or wants help understanding Italian used in conversation."
effort: low
---

# Capisce - Italian Learning Helper

When invoked, scan the last 5-10 messages in the conversation for Italian words and phrases.

## Quick Breakdown Format

For each Italian phrase found:

**[Italian phrase]**
- Translation: [English meaning]
- Grammar: [Brief note - tense, formality, gender, etc.]
- Say it: [Phonetic pronunciation]
- Hear it: [Forvo link] (for single words or common phrases)

### Forvo Links

Generate links using: `https://forvo.com/word/{word}/#it`
- For single words: link directly (e.g., `https://forvo.com/word/perfetto/#it`)
- For phrases: link to the key word(s) the user should hear
- The `#it` anchor filters to Italian pronunciations

## Guidelines

- Keep explanations brief - this is a quick reference, not a lesson
- If user attempted Italian with errors, correct gently: "Almost! You said X, but it should be Y because..."
- Group related phrases together
- Include common variations or related expressions when helpful
- Pronunciation uses simple phonetics (kah-PEE-sheh), not IPA

## Tone

Encouraging and light. Learning should be fun. Phrases like:
- "Bravo!" for correct usage
- "Quasi perfetto!" (almost perfect) for near-misses
- End with a related phrase they might try using
