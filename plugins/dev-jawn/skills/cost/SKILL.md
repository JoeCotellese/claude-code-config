---
name: cost
max_words: 450
effort: low
description: "Token pressure report. Invoke with `/cost #<issue>` for one issue's weighted tokens by phase, or `/cost` for the current session's tokens per issue. Also triggers on 'how much did #N cost', 'token pressure', 'where did the tokens go'. Reads Claude Code transcripts read-only and falls back to the issue's committed snapshot when the transcripts are gone."
---

<!-- ABOUTME: /cost: weighted tokens per dev-jawn issue and phase, or per issue for the current session. -->
<!-- ABOUTME: Thin wrapper over scripts/cost/cost.py; prints its report verbatim and never writes transcripts. -->

# Cost

Shows where an issue's tokens went: per phase, main session against subagents, advisor calls,
peak context, and the share spent above 200K context. Works from any session in any repo.

## Run

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cost/cost.py" $ARGUMENTS --session-id "${CLAUDE_SESSION_ID}"
```

Print stdout verbatim in a code block. Add nothing to the figures and do not recompute them.

- **Exit 0:** a report, a "nothing found" line, or a written snapshot. Print it as is.
- **Exit 1:** a transcript the parser cannot read. Stderr names `file:line` and the reason.
  Report that line and stop. A partial report would mislead, so never estimate figures.
- **Exit 2:** bad arguments. Show the usage line.

## Reading the report

- **Weighted tokens:** every model's tokens scaled to Opus 5.5 input tokens by price, so models
  compare on one scale. Directional: rankings matter, totals are within about 20%.
- **advisor:** tokens from advisor calls, counted at the advisor model's weight.
- **attempts:** how many times the phase was entered. Two or more prints a rework note.
- **peak ctx / over 200K:** the largest single context and the share of weighted tokens spent
  above 200K context. High shares point at unbounded context growth.
- **top pressure:** the agent with the most weighted tokens above 200K.
- **unattributed:** tokens no issue binding covers. They are never dropped from a total.

## Flags

- `--summary`: the one line autopilot's final report carries.
- `--snapshot`: writes `.dev-jawn/cost/<N>.json`. Only `/submit` runs this.
- `--offline`: skip the `gh` outcome lookup.
- `--project GLOB`: also count project dirs whose recorded cwd matches, for moved checkouts.

## Rules

- Never write under `~/.claude/projects`. The script only reads it.
- `/cost` never binds its own session to an issue, so running it mid-run is safe.
