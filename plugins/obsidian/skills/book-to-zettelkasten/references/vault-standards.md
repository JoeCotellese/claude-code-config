# Obsidian Vault Standards Reference

## Vault Location
`/Users/joec/obsidian-vault/`

## Folder Structure
- `2_Literature Notes/` - Book summaries, article notes (source-level notes)
- `3_Permanent Notes/` - Atomic, evergreen concept notes (idea-level notes)
- `Templates/` - Note templates

## Literature Note Convention
- Filename: `bookx - Title.md` (existing convention for books)
- Purpose: Reading log and chapter-by-chapter index; links out to permanent notes

## Permanent Note Convention
- Filename: Descriptive title WITHOUT timestamps (e.g., `Whole Product Strategy.md`)
- One atomic idea per note
- Linked together via `[[wiki-links]]`

## Frontmatter (Required)
```yaml
---
tags:
  - type/note  # or type/book for literature notes
  - domain-tag-1
  - domain-tag-2
created: "YYYY-MM-DD, HH:MM"
updated: "YYYY-MM-DD, HH:MM"
---
```
- Tags use list format (with dashes), not comma-separated
- Always include at least one `type/` tag plus relevant domain tags
- Common domain tags: `productmanagement`, `business`, `psychology`, `engineering`, `ai`, `philosophy`

## Standard Content Sections (Permanent Notes)
Every permanent note ends with these three sections:

```markdown
## Questions
- Open questions or areas for further exploration

## Terms
- [[Wiki Link]] to related concept notes

## References
- [[bookx - Source Book]] - Author (chapter reference)
- External sources
```

## Wiki-Link Syntax
- Internal links: `[[Note Title]]`
- Aliased links: `[[Full Note Title|Display Text]]`
- Obsidian URL for clickable links: `obsidian://open?vault=obsidian-vault&file=PATH%2FTO%2FFile.md`

## Tagging Taxonomy
### Content Type Tags (type/ prefix)
- `type/note` - General atomic notes
- `type/book` - Book-specific notes
- `type/literature` - Book/article summaries
- `type/term` - Definitions/glossary

### Common Domain Tags
- `productmanagement`, `ux-design`, `engineering`, `business`
- `ai`, `psychology`, `productivity`, `philosophy`
- `behavior`, `cognitive-bias`, `meditation`
