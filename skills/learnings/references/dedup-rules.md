# Deduplication Rules

Two developers working the same repo will generate overlapping learnings. The skill must detect duplicates by *meaning*, not string equality.

## Three Outcomes

For each candidate vs. the existing Active set, pick one:

1. **Drop** — an equivalent entry exists; skip silently
2. **Refine** — an existing entry is close but the candidate is better; update in place
3. **Add** — no meaningful overlap; append as new

## Drop Rules (Exact or Near-Exact Match)

Drop the candidate if an existing entry meets **any**:

- Same symbol and ≥80% token overlap after lowercasing and stripping punctuation
- Same symbol and the core noun phrase is identical (e.g. both about "pgvector over Qdrant")
- The candidate is a weaker restatement (less specific, same conclusion)

Do not tell the user about every drop; report a count at the end.

## Refine Rules (Semantic Duplicate, Better Wording)

Refine when the candidate and an existing entry share a conclusion but the candidate adds:

- A more specific rationale ("— ops simplicity wins" vs. no reason)
- A more precise location (`core::repo` vs. "the core module")
- A corrected detail (the old entry was slightly wrong)

Refinement action:
- Replace the existing entry's text with the candidate's text
- Bump the date to today
- Move it to the top of Active (newest-first)
- Report to the user: "Refined entry from YYYY-MM-DD: <old> → <new>"

## Add Rules (Genuinely New)

Add if none of the above triggers. New entries go at the top of Active with today's date.

## Contradiction Handling

If the candidate **contradicts** an existing entry (same topic, opposite conclusion):

- **Do not silently overwrite.**
- Surface both entries to the user and ask which is correct:
  - Replace the old entry with the new
  - Keep both (rare — usually means the topic needs splitting)
  - Drop the candidate and keep the old
- Contradictions often mean a real decision reversal; worth a moment of human attention.

## Semantic Similarity Signals

Without running embeddings, use these heuristics in the LLM dedup pass:

- Do both entries name the same library, file, module, or command?
- Do both entries advocate the same choice or warn about the same trap?
- Would a reader skimming the file find them redundant?

If yes to any two of the above, treat as duplicate or refinement candidate.

## Cross-Symbol Rules

Usually dedup only within the same symbol. Exceptions:

- 🧩 pattern + 🔧 tooling can overlap ("always use CONCURRENTLY" as both a pattern and a tooling tip). Prefer 🪤 gotcha if it's a trap, else 🧩 pattern for conventions. Pick one, merge content.
- ⚖️ decision should not duplicate 🧩 pattern. A decision *creates* a pattern; once the pattern exists, the decision entry can be archived.

## Confidence Threshold

When dedup confidence is low (candidate might or might not duplicate an existing entry):

- Present both to the user alongside the new candidates
- Let the user decide
- Default to **add** if the user doesn't answer — additive mistakes are cheaper than lost context
