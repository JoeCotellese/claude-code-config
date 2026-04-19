# LEARNINGS.md Format Specification

## Canonical File Layout

```markdown
# Learnings — <project-name>

Durable project knowledge. One line per entry. Curated by humans and AI via the `/learnings` skill.

Legend: ⚖️ decision · 🪤 gotcha · 🧩 pattern · 🔧 tooling
Format: `YYYY-MM-DD SYMBOL one-line learning (≤100 chars)`

## Active

2026-04-19 ⚖️ Chose pgvector over Qdrant — ops simplicity wins at our scale
2026-04-18 🪤 CREATE INDEX blocks writers; always use CONCURRENTLY in migrations
2026-04-17 🧩 Repository trait in `core::repo`; concrete impls in `storage/*`
2026-04-15 🔧 `sqlx::query!` needs DATABASE_URL at compile; CI sets throwaway URL

## Archived

<entries older than 90 days or explicitly retired — newest first>
```

## Hard Rules

1. **One line per entry.** No continuations, no sub-bullets, no wrapping.
2. **≤100 characters per entry** including date and symbol. Compress ruthlessly.
3. **Date format:** `YYYY-MM-DD`. Always at the start.
4. **Symbol immediately after date**, from the legend only. No custom symbols.
5. **Newest first** within `## Active`.
6. **Two top-level sections only:** `## Active` and `## Archived`. Do not introduce subcategories — the symbol is the category.
7. **No blank lines between entries.** Blank line separates sections only.

## Symbol Meanings

| Symbol | Category | Use when |
|---|---|---|
| ⚖️ | Decision | A choice was made with rationale; future work should respect it |
| 🪤 | Gotcha | A trap that caused or will cause bugs; warn future devs |
| 🧩 | Pattern | A convention to follow; "this is how we do X here" |
| 🔧 | Tooling | A non-obvious command, config, or workflow step |

## Good Entries

```
2026-04-19 ⚖️ Chose pgvector over Qdrant — ops simplicity wins at our scale
2026-04-18 🪤 CREATE INDEX blocks writers; always use CONCURRENTLY in migrations
2026-04-17 🧩 Repository trait in `core::repo`; concrete impls in `storage/*`
2026-04-15 🔧 `sqlx::query!` needs DATABASE_URL at compile; CI sets throwaway URL
```

Why they work: specific, actionable, contain the "why" or the "where", under 100 chars.

## Bad Entries (do not write these)

```
2026-04-19 ⚖️ We discussed several database options and eventually picked pgvector because of various factors
```
Too long, vague ("various factors"). Compress to ≤100 chars with the real reason.

```
2026-04-19 🧩 Write good code
```
Useless. Not a project-specific pattern.

```
2026-04-19 🪤 Bug in login flow
```
Not a learning — a TODO. Belongs in an issue, not LEARNINGS.md.

```
2026-04-19 🔧 Uses Rust
```
Already obvious from the codebase. Not a learning.

## Entry Editing

When updating an existing entry in place (semantic duplicate refinement):
- Bump the date to today
- Rewrite the text if clearer
- Move it to the top of `## Active` (newest-first ordering)

## Archive Transitions

- `/learnings review` moves entries older than 90 days from Active to Archived
- Archived entries keep original date
- Archived is append-only from the review workflow's perspective; manual edits allowed
