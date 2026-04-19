# Extraction Heuristics

How to decide what from a conversation qualifies as a learning. **Bias toward extracting nothing** — a noisy LEARNINGS.md is worse than a sparse one.

## The Four Tests

A conversation fragment is a candidate only if it passes all four:

1. **Durable.** Will this still be true in 6 months? Session-specific progress is not durable.
2. **Project-specific.** Does it describe *this* project? Generic advice belongs in global config, not LEARNINGS.md.
3. **Non-obvious.** Would a new collaborator discover this quickly from the code/README? If yes, skip.
4. **Compressible to ≤100 chars.** If you can't say it in one line, it's documentation, not a learning.

## Category Rubric

### ⚖️ Decision

A choice was made between real alternatives, with rationale, and the project now operates on that choice.

**Signals in conversation:**
- "We decided to…", "Let's go with…", "Chose X over Y because…"
- A debate that resolved
- A tradeoff explicitly named

**Extract if:** the decision constrains future work.
**Skip if:** the decision was to do the default thing, or the decision was trivial.

### 🪤 Gotcha

A non-obvious trap that caused or would cause a bug.

**Signals:**
- "Turns out X doesn't work when…", "Silently fails if…", "Bit us because…"
- A surprising behavior of a library, tool, or config
- An edge case that isn't documented where you'd expect

**Extract if:** someone stepping on this trap would lose real time.
**Skip if:** it's a one-off bug already fixed with no recurrence risk, or it's covered by tests.

### 🧩 Pattern

An established convention the project follows; "how we do X here".

**Signals:**
- "We always put X in…", "Our convention is…", "All Y should use Z"
- A repeated shape that appears in multiple places
- An architectural rule

**Extract if:** a new contributor would write code the wrong way without this guidance.
**Skip if:** the pattern is already enforced by tooling (linter, type system, CI).

### 🔧 Tooling

A non-obvious command, script, env var, or workflow step that's part of working on this project.

**Signals:**
- "To do X, run…", "You need to set ENV_VAR=…", "Before first build, do Y"
- A local dev workflow that isn't in the README
- A debugging trick that repeatedly helps

**Extract if:** the tool/command is specific to this project and not self-evident.
**Skip if:** it's standard for the ecosystem (e.g. "run `cargo test`").

## Strong Skip Signals

Do not extract if any apply:

- The fragment is purely about Claude's own behavior (belongs to `/kaizen`)
- The fragment is a session recap or debugging narrative (belongs to `/log`)
- The user sounds uncertain ("maybe", "I think", "we might")
- The information lives better as a code comment at a specific file:line
- It's a TODO, not a truth

## Compression Technique

When a candidate passes the four tests but runs long:

1. Drop throat-clearing ("we decided that…", "it turns out that…")
2. Replace full sentences with sentence fragments
3. Use backticks for code identifiers
4. Lead with the *conclusion*, append the *reason* after an em dash

Example:
- Before (145 chars): "We decided after discussion that pgvector is the right choice over Qdrant because managing a separate service isn't worth it at our scale"
- After (67 chars): "Chose pgvector over Qdrant — ops simplicity wins at our scale"

## When in Doubt

Present the candidate to the user with a note like "borderline — worth recording?" rather than silently dropping or silently including. The user is the final filter.
