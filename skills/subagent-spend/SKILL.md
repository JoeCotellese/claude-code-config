---
name: subagent-spend
effort: low
description: Measure which models and effort levels Claude Code subagents actually ran on, and what they cost, from local JSONL transcripts. Use when the user asks "what model is my Explore agent running", "what are my subagents costing", "did that config change save anything", "baseline my token usage", or wants a before/after on CLAUDE_CODE_SUBAGENT_MODEL or a custom agent's model/effort.
user_invocable: true
trigger: /subagent-spend
arguments: "[mark <name> | report [--since <name>] [--until <name>]]"
---

# Subagent Spend

Claude Code logs every subagent turn locally. Each session writes
`~/.claude/projects/<project>/<session>.jsonl`, and each subagent gets its own
file under a sibling `subagents/` directory. Assistant lines carry `model`,
`effort`, `timestamp`, and full `usage`. This skill joins those files back to the
agent type that spawned them, so you can see what `Explore` or a custom agent
really ran on rather than what people assume it runs on.

## Commands

Baseline before changing anything:

```bash
python3 scripts/subagent_spend.py mark baseline
```

That writes `~/.claude/spend-snapshots/baseline.json`: a UTC cutoff plus the
config that produced the numbers up to it (`CLAUDE_CODE_SUBAGENT_MODEL`,
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `ANTHROPIC_MODEL`, the model and effort in
every `~/.claude/agents/*.md`, and the Claude Code version).

Then change config, work for a while, and measure only what happened after:

```bash
python3 scripts/subagent_spend.py report --since baseline
```

Other forms:

- `report` with no window: all time.
- `--since` / `--until` accept a snapshot name or a raw ISO-8601 UTC timestamp.
- `--json` for machine-readable rows.

Output is grouped by agent type, then by model and effort: turns, input tokens,
cache-write, cache-read, output tokens, dollars, plus runs and dollars per run.

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
