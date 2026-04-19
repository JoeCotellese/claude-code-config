# Learnings Skill

Curate durable project knowledge into a shared `LEARNINGS.md` at the repo root. Designed for small teams (2+ devs) sharing context on a single codebase, where claude-mem's per-user memory isn't visible to collaborators.

## Why This Exists

`claude-mem` captures cross-session memory per user. Great for solo work, useless for teammates who don't share your database. `LEARNINGS.md` solves the shared-context problem with plain markdown committed to the repo — readable by humans, future-proof against any tooling changes, and portable across AI assistants.

## When to Use It

Use `/learnings` on a project when:
- Two or more devs work the same repo and need shared durable context
- You want decisions, gotchas, and conventions to survive tool changes
- You want the file reviewable in PRs

Skip it when:
- You're solo and already use `claude-mem` — redundant
- The project is short-lived or experimental
- You'd rather lean on code comments and ADRs exclusively

## What It Captures

Four categories, one line each, ≤100 chars:

- ⚖️ **Decisions** — choices with lasting consequences
- 🪤 **Gotchas** — traps that bit us or will bite teammates
- 🧩 **Patterns** — conventions to follow
- 🔧 **Tooling** — non-obvious commands, configs, or workflow steps

Anything that can't compress to one line is documentation, not a learning, and belongs in the codebase.

## How It Works

### 1. Opt the project in

From inside any git repo, run:

```
/learnings init
```

This creates at the repo root:
- `.learnings.toml` — opt-in marker plus config (`max_active`, `archive_after_days`)
- `LEARNINGS.md` — the shared file, with legend and empty `## Active` / `## Archived` sections

It will also suggest appending `@LEARNINGS.md` to your project's `CLAUDE.md` so future sessions auto-load the file as context. Without that line, the file is write-only — it won't come back into the next session.

### 2. Capture learnings during work

Two invocation styles:

| Command | Behavior |
|---|---|
| `/learnings` | Scans recent conversation, proposes candidates, asks for confirmation, writes accepted ones |
| `/learnings "<text>"` | Records the user's quoted text verbatim as one entry |

Every candidate is classified, compressed, deduped against existing entries, and shown to the user before anything is written. Nothing is written silently.

### 3. Curate periodically

Run this when the file gets crowded or entries go stale:

```
/learnings review
```

- Moves entries older than `archive_after_days` from `## Active` to `## Archived`
- Flags potential semantic duplicates in Active for human review
- Warns if Active exceeds `max_active`

### 4. Share via git

`LEARNINGS.md` and `.learnings.toml` live at the repo root. Commit them. Push. Teammates pull. The skill's dedup pass prevents conflicts when two devs capture the same learning on separate branches.

## File Format

```markdown
# Learnings — <project-name>

Legend: ⚖️ decision · 🪤 gotcha · 🧩 pattern · 🔧 tooling
Format: `YYYY-MM-DD SYMBOL one-line learning (≤100 chars)`

## Active

2026-04-19 ⚖️ Chose pgvector over Qdrant — ops simplicity wins at our scale
2026-04-18 🪤 CREATE INDEX blocks writers; always use CONCURRENTLY in migrations
2026-04-17 🧩 Repository trait in `core::repo`; concrete impls in `storage/*`

## Archived
```

Hard rules: newest first, one line per entry, ≤100 chars, symbol from the legend only. See `references/format-spec.md` for the full spec.

## Guardrails

- Never writes without user confirmation (except verbatim `/learnings "<text>"`)
- Never fabricates a learning — only captures things actually discussed
- Never touches files outside the repo root
- Aborts if `.learnings.toml` has `enabled = false`
- Verbatim entries are preserved exactly — no paraphrasing

## Files in This Skill

```
learnings/
├── SKILL.md                         # main instructions, 4 subcommands
├── README.md                        # this file
├── references/
│   ├── format-spec.md               # canonical file layout, hard rules
│   ├── extraction-heuristics.md     # 4-test rubric for what qualifies
│   └── dedup-rules.md               # drop / refine / add / contradict
└── scripts/
    └── init-project.sh              # bootstraps .learnings.toml + LEARNINGS.md
```

## Relationship to Other Skills

| Skill | Target | Output |
|---|---|---|
| `/learnings` | Project/domain knowledge, shared | `<repo>/LEARNINGS.md` |
| `/log` | Debugging progression, solo notebook | `<vault>/Dev Log — <project>.md` |
| `/kaizen` | Claude harness/config friction | `~/.claude/*`, CLAUDE.md, skills |

All three read the same conversation; they extract different things for different audiences.
