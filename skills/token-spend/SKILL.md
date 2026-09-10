---
name: token-spend
effort: low
description: Inventory Claude Code token usage from local JSONL transcripts - by tool, by skill, by agent type, by model and effort. Use when the user asks "which tool is eating my context", "does this skill actually save tokens", "what model is my Explore agent running", "what are my subagents costing", "did that config change save anything", or wants a before/after on a skill, a hook, CLAUDE_CODE_SUBAGENT_MODEL, or a custom agent's model/effort.
user_invocable: true
trigger: /token-spend
arguments: "[mark <name> | report [--since <name>] | tools [--since <name>]]"
---

# Token Spend

Claude Code logs every subagent turn locally. Each session writes
`~/.claude/projects/<project>/<session>.jsonl`, and each subagent gets its own
file under a sibling `subagents/` directory. Assistant lines carry `model`,
`effort`, `timestamp`, and full `usage`. This skill joins those files back to the
agent type that spawned them, so you can see what `Explore` or a custom agent
really ran on rather than what people assume it runs on.

## Commands

Baseline before changing anything:

```bash
python3 scripts/token_spend.py mark baseline
```

That writes `~/.claude/spend-snapshots/baseline.json`: a UTC cutoff plus the
config that produced the numbers up to it (`CLAUDE_CODE_SUBAGENT_MODEL`,
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `ANTHROPIC_MODEL`, the model and effort in
every `~/.claude/agents/*.md`, and the Claude Code version).

Then change config, work for a while, and measure only what happened after:

```bash
python3 scripts/token_spend.py report --since baseline
```

Other forms:

- `report` with no window: all time.
- `--since` / `--until` accept a snapshot name or a raw ISO-8601 UTC timestamp.
- `--json` for machine-readable rows.
- `--csv <path>` for a spreadsheet, or `--csv -` for stdout. Both `report` and
  `tools` take it. Every row carries the window bounds, so two runs concatenate
  into one before/after sheet; the `tools` CSV adds a `kind` column
  (`tool`, `skill`, `mcp-tool`, `non-tool`) for pivoting.

Output is grouped by agent type, then by model and effort: turns, input tokens,
cache-write, cache-read, output tokens, dollars, plus runs and dollars per run.

The first group is `main-session (not a subagent)` — the turns you drive
yourself, read from the top-level session transcripts, counted per session
instead of per run. Sidechain lines in those files are skipped (older Claude
Code versions wrote subagent work into the parent transcript), and turns are
deduplicated by `uuid` so a resumed or forked session does not count twice. The
`TOTAL` line splits main-session from subagents and gives the subagent share.

That share is the number to look at first. `CLAUDE_CODE_SUBAGENT_MODEL`, agent
`model`, and agent `effort` only touch the subagent slice; if subagents are 14%
of your bill, a perfect subagent config change caps out at 14%.

## Inventory by tool and skill

```bash
python3 scripts/token_spend.py tools --since baseline
```

One row per tool, per skill (`Skill:dev-jawn:ready`, body included - a skill's
SKILL.md arrives as the user text right after its tool result), and per MCP tool,
with `--by-model` to split each row by model and effort. Useful flags:
`--session <substring>` to scope to a single transcript for an A/B, `--project`
to scope to one repo, `--main-only` to exclude subagent transcripts.

Two columns, and the second is the one that matters:

- **added** - tokens the item put into context.
- **carry** - those same tokens re-read on every later turn of that session.

A 20K-token result on turn 3 of a 200-turn session is not a 20K-token decision;
it is read ~197 more times. That is why `Read` dominates the ranking while `Edit`
barely registers, and why a skill that loads 18K of instructions early costs more
than its size suggests.

**Attribution is character-based, not billed tokens.** A turn's
`cache_creation_input_tokens` re-counts the whole prefix whenever the 5-minute
cache TTL lapses, so billed input genuinely cannot be split across the items that
caused it. The footer prints what the estimate covers against measured input for
the same window - typically around a third; the remainder is system prompt, tool
schemas, and cache re-creation, none of which belongs to any single tool. Use the
ranking and the before/after delta, not the absolute dollars.

## Testing whether a skill saves tokens

Run the work once without the skill and once with it, then compare the same
session-scoped inventory:

```bash
python3 scripts/token_spend.py tools --session <before-session-id>
python3 scripts/token_spend.py tools --session <after-session-id>
```

Compare `added` and `carry` for the tools the skill was meant to displace (`Read`
and `Bash`, usually) against the skill's own row. A skill that costs 18K to load
and saves two 40K file reads wins; one that saves a single `Grep` does not.

## Reading the results

Three things to get right when reporting a before/after:

- **Compare dollars per run and the model mix, not window totals.** Different
  weeks carry different workloads, so absolute spend moves for reasons that have
  nothing to do with the config change.
- **Cache reads dominate.** Most of the bill is `cache_read` at 0.1x input, not
  output tokens. A change that lowers turn count but raises re-reads can cost
  more.
- **`unknown` is real work, not an error.** A subagent transcript lands there
  when its spawning `Task` call lives in a parent transcript that has since
  rotated away. Those runs still cost money; never quote a total as complete
  without saying how much sits in `unknown`.

## Prices

`PRICES` in the script is per-MTok input/output, with cache write at 1.25x input
and cache read at 0.1x input. Dated model snapshots (`claude-haiku-4-5-20251001`)
normalize to their base ID. A model missing from the table counts as $0 and the
report prints a WARNING naming it — add the row rather than ignoring the warning.

## Verifying a change landed

Re-run `mark` after the config change. Diff the two snapshots' `config` blocks to
confirm the environment actually carried the setting into the sessions you are
measuring; a shell that never exported the variable produces an honest-looking
report of no change.
