---
name: book-to-zettelkasten
description: Decompose books into atomic Zettelkasten permanent notes in the Obsidian vault. Invoke with `/book-to-zettelkasten` or when user says "ZK this book", "atomize this book", "extract permanent notes from this book", "decompose book into notes", "break this book into ZK notes", or wants to turn a book summary or full book text into linked atomic concept notes. Also use when user has an existing literature note they want to enrich with permanent notes, or when they paste book content and want it structured for their second brain.
---

# Book to Zettelkasten

Decompose a book's content into atomic, interlinked permanent notes following Zettelkasten methodology. The input can be full book text, chapter excerpts, or an existing literature note. The output is a set of permanent notes in `3_Permanent Notes/` plus an updated or new literature note in `2_Literature Notes/`.

Read [references/vault-standards.md](references/vault-standards.md) for Obsidian vault formatting standards before creating any notes.

## Workflow

### Phase 1: Gather Context

1. **Identify the book** - Title, author, subject domain
2. **Check for existing notes** - Search the vault:
   - `Grep` for the book title across `**/*.md`
   - `Glob` for filename matches in `2_Literature Notes/` and `3_Permanent Notes/`
3. **Read existing literature note** if one exists - understand what's already captured
4. **Determine input type**:
   - Full book text pasted by user → proceed to analysis
   - Existing literature note only → read it, ask user if they have additional source text
   - Chapter excerpts → work with what's available, note gaps

### Phase 2: Analyze and Propose Structure

Extract concepts from the book at three tiers:

**Tier 1 - Core Frameworks** (always extract these first)
- The book's central models, theories, or frameworks
- Ideas that stand alone as reusable mental models
- Typically 4-8 notes per book

**Tier 2 - Supporting Concepts** (extract when the book has rich character/profile content)
- Taxonomies, profiles, archetypes described in the book
- Typologies the author uses to categorize people, situations, or strategies
- Typically 3-6 notes per book

**Tier 3 - Tactical Methods** (extract when the book provides actionable procedures)
- Step-by-step methods, checklists, or frameworks for action
- Decision-making tools or evaluation criteria
- Typically 2-4 notes per book

**Present the proposed structure to the user before creating notes.** Show:
- Proposed note titles organized by tier
- One-line description of what each captures
- Estimated total note count

Wait for user approval before proceeding.

### Phase 3: Create Permanent Notes

For each approved note, write to `3_Permanent Notes/` following this structure:

```markdown
---
tags:
  - type/note
  - domain-tag-1
  - domain-tag-2
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
---

# [Concept Title]

[1-3 sentence definition/summary of the concept in the author's voice distilled to its essence]

## [Core content sections - vary by concept type]

[Use tables, blockquotes, lists as appropriate. Prefer tables for comparisons
and profiles. Use blockquotes for key author quotes that crystallize the idea.
Keep content dense but scannable.]

## Questions
- [Open questions connecting this concept to the reader's world]
- [Areas for further exploration]
- [How does this relate to other domains?]

## Terms
- [[Related Concept Note]]
- [[Another Related Note]]

## References
- [[bookx - Book Title]] - Author (Chapter X)
- [Other sources if applicable]
```

**Content principles:**
- **Atomic**: One concept per note. If you're writing "and also..." it's probably two notes.
- **Evergreen**: Write as timeless knowledge, not "Moore says in Chapter 3..."
- **Dense**: Use tables for structured comparisons. Use blockquotes for the author's best lines. No filler.
- **Interlinked**: Every note should link to 2-5 other notes from the same book. Use `[[wiki-links]]` for notes that exist and `[[Proposed Title]]` for ones being created in the same batch.
- **Aliased links**: Use `[[Full Title|Short Display]]` when the full title is unwieldy inline.
- **Questioning**: End with 2-4 genuine questions that connect the concept to the reader's domain or to other books in the vault.

**What NOT to include:**
- Chapter numbers or "according to the author" framing
- Exhaustive examples from the book (pick 2-3 best ones)
- Content that merely summarizes plot/narrative without extracting a reusable idea

### Phase 4: Create or Update Literature Note

**If creating new:** Write to `2_Literature Notes/bookx - [Title].md` with:
- Book metadata frontmatter (tags including `type/book`, author, domain tags, created/updated)
- Cover image if available
- Author wiki-link
- Auto-generated summary
- **Core Concepts section** at top linking all permanent notes, organized by tier
- Chapter-by-chapter summaries with key points
- **Terms section** at bottom listing all permanent note wiki-links
- **References section** listing related works mentioned in the book

**If updating existing:** Add or update:
- Core Concepts section (add if missing, organized by tier)
- Wiki-links to new permanent notes throughout chapter summaries where relevant
- Terms section with all permanent note links
- Fix any frontmatter issues (missing created/updated, missing domain tags)
- Do NOT remove existing content - only augment

### Phase 5: Verify Cross-Links

After all notes are created:
- Confirm every permanent note links back to the literature note
- Confirm every permanent note links to at least 2 sibling permanent notes
- Confirm the literature note's Core Concepts section lists all permanent notes by tier
- Search the vault for existing permanent notes on related topics and suggest cross-links to user

## Handling Large Books

For books with 10+ potential permanent notes:
- Present Tier 1 first, get approval, create those
- Then present Tier 2 and 3, get approval, create those
- This avoids overwhelming the user and allows course-correction

## Handling Partial Input

When the user provides only a few chapters or a partial summary:
- Extract what you can from available material
- Note which tiers/concepts are likely missing
- Suggest what additional content would unlock more notes
- Create what's possible now; the user can invoke the skill again later with more content

## Example Invocations

- `/book-to-zettelkasten` (with book text pasted in the same message)
- "ZK this book" (with book text or after discussing a book)
- "I have a literature note for Thinking Fast and Slow, can you extract permanent notes from it?"
- "Atomize chapters 3-5 of this book" (with chapter text pasted)
