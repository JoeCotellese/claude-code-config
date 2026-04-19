---
name: learnings
description: "Curate durable project learnings into a shared LEARNINGS.md at the repo root. Invoke with /learnings or when the user says 'capture learning', 'record this decision', 'add to learnings'. Extracts one-line, dated, symbol-prefixed entries (decisions, gotchas, patterns, tooling) from recent conversation, dedupes against existing entries, and appends to <repo>/LEARNINGS.md. Supports subcommands: init (enable for project), review (prune/archive), and quoted verbatim entries."
effort: low
---

# Learnings Skill

Capture durable project knowledge as one-line, dated, symbol-prefixed entries in `<repo>/LEARNINGS.md`. The file is committed to the repo so human collaborators and AI assistants working in the project read the same context.

## Scope: What Belongs Here

- **Decisions** with lasting consequences (architecture choices, library picks, non-obvious tradeoffs)
- **Gotchas** — traps that bit us or would bite a teammate
- **Patterns** — established conventions others should follow
- **Tooling** — non-obvious commands, configs, or workflows that are part of the project

## Scope: What Does NOT Belong Here

- Session progress notes → use `/log`
- Claude harness/config issues → use `/kaizen`
- One-off debugging steps → use `/log`
- Things already documented in code comments, README, or ADRs
- Speculation, aspirations, "maybe we should"

If a candidate can't be compressed to a single ≤100-char line, it is not a learning — it is documentation. Tell the user to write it in the codebase instead.

## Subcommands

| Invocation | Behavior |
|---|---|
| `/learnings` | Scan recent conversation, extract candidates, confirm, append |
| `/learnings "<text>"` | Record the user's exact text verbatim as one entry |
| `/learnings init` | Create `.learnings.toml` + `LEARNINGS.md` scaffold; offer to wire `@LEARNINGS.md` into project CLAUDE.md |
| `/learnings review` | Archive stale entries (>90d), flag potential duplicates for user review |

## Preconditions

1. Current working directory is inside a git repository. If not, abort with a message.
2. The project is opted in: `.learnings.toml` exists at the repo root.
   - If missing and the user invokes a non-init subcommand, ask whether to run `/learnings init` first.
3. `LEARNINGS.md` lives at the repo root alongside `.learnings.toml`.

## Default Workflow (`/learnings`)

### Step 1: Locate repo root

```bash
git rev-parse --show-toplevel
```

Abort if not a git repo. Store as `REPO_ROOT`.

### Step 2: Verify opt-in

If `$REPO_ROOT/.learnings.toml` does not exist, ask the user:

> This project isn't set up for learnings yet. Run `/learnings init` first?

Do not proceed without confirmation.

### Step 3: Load existing entries for dedup

Read `$REPO_ROOT/LEARNINGS.md`. Parse the `## Active` section into memory. This is the dedup corpus — see `references/dedup-rules.md`.

### Step 4: Extract candidates

Scan the last 15-25 messages for learning candidates per `references/extraction-heuristics.md`. Be strict — prefer zero candidates over noisy ones.

### Step 5: Classify and compress

For each candidate:
- Assign a symbol: ⚖️ decision, 🪤 gotcha, 🧩 pattern, 🔧 tooling
- Compress to ≤100 chars, one line
- If compression loses the essence, drop the candidate

### Step 6: Dedup pass

For each candidate, apply rules in `references/dedup-rules.md`:
- Exact match → drop
- Semantic duplicate → propose updating the existing entry in place
- Contradicts an existing entry → flag to user, do not silently overwrite

### Step 7: Present and confirm

Show all candidates in a single batch for user review. Let the user accept, reject, or edit before writing. Never write without confirmation.

### Step 8: Write

Insert accepted entries under `## Active`, newest first, with today's date in `YYYY-MM-DD` format. Preserve file formatting per `references/format-spec.md`.

Report what was added, what was updated, what was skipped.

## Verbatim Workflow (`/learnings "<text>"`)

When the user supplies quoted text:
- Record the text **exactly as provided**. Do not paraphrase, shorten, or rewrite.
- The user still picks (or you propose) a symbol. Ask if ambiguous.
- Dedup pass still runs — if the verbatim text duplicates an existing entry, tell the user and stop.

## Init Workflow (`/learnings init`)

Run `scripts/init-project.sh` from the skill directory. It will:

1. Create `$REPO_ROOT/.learnings.toml` with defaults
2. Create `$REPO_ROOT/LEARNINGS.md` with legend header and empty sections
3. Offer (but do not force) to append `@LEARNINGS.md` to `$REPO_ROOT/CLAUDE.md` so entries auto-load into future sessions

Do not overwrite existing files. If either exists, report and skip that step.

## Review Workflow (`/learnings review`)

1. Parse `LEARNINGS.md`. Move entries in `## Active` older than 90 days to `## Archived` (newest archived first).
2. Scan remaining Active entries for semantic duplicates per `references/dedup-rules.md`. Present clusters to the user; let them merge or keep.
3. If Active exceeds 100 entries, warn and suggest manual curation.

## Guardrails

- **Never** fabricate a learning. Only record things actually decided, observed, or discussed in the conversation (or provided verbatim).
- **Never** remove an Archived entry without explicit user instruction.
- **Never** write without user confirmation, except when the user passes verbatim text via `/learnings "<text>"`.
- **Never** touch `LEARNINGS.md` outside the repo root.
- If `.learnings.toml` disables the skill (`enabled = false`), abort.

## References

- `references/format-spec.md` — canonical file format and examples
- `references/extraction-heuristics.md` — what qualifies as a learning
- `references/dedup-rules.md` — duplicate detection and resolution
