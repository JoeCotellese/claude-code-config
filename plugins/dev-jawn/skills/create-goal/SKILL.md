---
name: create-goal
effort: medium
description: "Author a `/goal` agentic loop. Invoke with `/create-goal <what you want to run>` or when the user says 'create a goal', 'write a loop', 'make this run unattended', 'how do I loop this', 'what should my exit condition be'. Routes away first if the job actually wants /loop, a fresh-context Agent, or a skill. Then drives the exit condition to something a tool-less evaluator can judge, picks a cap, and prints a paste-ready /goal plus a loop card. Writes nothing to disk."
---

# Create Goal

Turn "I want this to keep running until it's done" into a `/goal` that actually stops at the
right moment.

## The one rule everything follows

From `${CLAUDE_PLUGIN_ROOT}/skills/WORKFLOW.md`:

> The `/goal` evaluator **does not call tools**. It only judges what has been printed into the
> conversation.

So an exit condition is good enough when **a reader holding no tools, seeing only the
transcript, can decide PASS or FAIL by finding a literal string.** Every question below exists
to get the author to that point. When in doubt, apply that test and say the result out loud.

## Input

Take whatever the user supplied as the brief. Ask only about what is genuinely missing: if the
brief already answers a question below, restate the answer as an assumption instead of asking
it again. Batch remaining questions with AskUserQuestion, at most four per call, recommended
option first.

## Step 0 — Routing gate

Ask this before anything else. Picking the wrong primitive is the most common mistake, and the
interview is wasted if the answer was never `/goal`.

> What are you waiting on, and who moves it?

- **You or the agent moves it** (code gets fixed, tests go green, a document gets written)
  → `/goal`. Continue to Step 1.
- **Someone else moves it, on their schedule** (CI finishing, PR comments arriving, a
  colleague replying) → `/loop`. Stop. Print the WRONG PRIMITIVE block.
- **Nothing moves; work that already happened needs an independent grader** → a fresh-context
  `Agent` call. The builder never grades its own work. Stop. Print the WRONG PRIMITIVE block.
- **It is a standing rule, not a loop** ("always run ruff before committing") → that is a
  skill or a hook. Stop. Print the WRONG PRIMITIVE block.

The trap: "keep checking until CI is green" sounds like a goal and is not. You are not the one
turning it green, so re-running yourself changes nothing. That is `/loop`.

## Step 1 — The body

> What does one iteration do?

One or two sentences. If the answer is a whole project rather than a repeatable step, the loop
is too big; say so and help split it.

## Step 2 — The exit, in the user's own words

> How will you know it's done?

Capture the answer verbatim. Do not clean it up yet. The next step needs the raw wording to
classify it.

## Step 3 — Classify the exit condition

Three tiers. Drive every answer to tier 2.

**Tier 0, rejected. Subjective.** There is no fact of the matter.

Fires on: clean, good, solid, better, right, nice, readable, robust, sensible, intuitive,
polished, "feels", "looks".

Example: "until the code is clean."

**Tier 1, rejected. Objective but unprintable.** True or false in the world, but the evaluator
cannot see the world. The agent asserts it and the loop closes on a claim rather than evidence.

Fires on: bare "the tests pass", "it works", "it's correct", "it's done", "the file exists",
"CI is green", "the build succeeds", "no errors" — whenever nothing in the loop body prints
the result.

This is the tier that catches people. It feels rigorous. It is not.

**Tier 2, accepted.** A fixed-format line the loop body prints on every iteration.

Example: `FLAKE VERDICT: status=stable runs=3`.

For tier 0 and tier 1, print the REJECTED block, then repair: ask what command or step already
produces the answer, and make the loop body print its result in a fixed format. Name the line
`<THING> VERDICT:` to match the existing `DOR VERDICT` and `DOD VERDICT` convention.

Do not weaken the condition to make it printable. "Ranked by relevance" does not become
"returns results". If the user cannot say what would count, that is a real gap; surface it.

## Step 4 — The artifact

> What gets printed that proves Step 2, and which step prints it?

Both halves matter. A verdict line nobody emits is not an artifact.

If nothing in the loop prints anything and no command reports status, stop. Print the BLOCKED
block naming the emitting step that has to be added. **Do not print a `/goal`.** A goal whose
condition can never be observed is worse than no goal: it runs to the cap every time and you
learn nothing from it.

## Step 5 — The cap

Always both. Never turns alone.

- **Turn limit.** Ask how many attempts before they would want to look themselves. Estimate
  turns as attempts times turns-per-attempt, plus two. The existing loops sit at 4 to 8.
- **Circuit breaker.** The same failure N runs in a row stops the loop. Default N to 3,
  following L4 in `WORKFLOW.md`. Without this, a turn cap just buys more repetitions of one
  mistake.

If the user says the loop has no natural cap, force one. The only uncapped loop in
`WORKFLOW.md` is L3, and only because an approved plan bounds its task list. Absent that kind
of bound, a cap is mandatory.

## Step 6 — The failure route

> When the cap is hit, what happens?

Name where it goes: a phase, a person, or stop-and-report. Default to stop-and-report. Never
silent continuation.

## Output

Print both blocks. Exact headers.

```
LOOP CARD
  Name:       <short-name>
  Trigger:    <what starts an iteration>
  Body:       <what one iteration does>
  Exit:       <the tier 2 condition>
  Artifact:   <the exact line, and which step prints it>
  Cap:        <N turns, or same failure 3x>
  Closed by:  /goal evaluator
  On cap:     <route>

Paste this:
/goal <condition stated as a literal string match on the artifact>.
Report <what> and stop. Stop after <N> turns.
```

The `/goal` text must quote the artifact line, not describe it. "The transcript contains a line
beginning `FLAKE VERDICT:` whose status is stable" is a string match. "The test is stable" is
not.

### The refusal blocks

```
WRONG PRIMITIVE: this wants <primitive>, not /goal
  Why: <who moves the thing being waited on>
  Do this instead: <concrete next step>
```

```
REJECTED (tier 0): "<their words>"
  Why: <no fact of the matter | nothing prints it>
  Try: <proposed artifact-backed rewrite>
```

```
BLOCKED: no printed artifact
  The loop body has no step that reports status.
  Add: <the emitting step>
  Then re-run /create-goal.
```

Tier 1 uses the same REJECTED block with `(tier 1)`.

## Worked examples

All three are real loops in this config, worth reading when an example helps more than a rule.

- **Definition of Done**, L4 in `${CLAUDE_PLUGIN_ROOT}/skills/WORKFLOW.md`. Trigger is a `DOD VERDICT` with
  `route=/implement`; exit is `status=PASS`; cap is the turn limit plus a three-strike circuit
  breaker. The only loop that runs fully unattended, which is why `/verify` is forbidden from
  editing code: that would close the loop by removing the signal rather than by satisfying it.
- **`/ready`**, at `${CLAUDE_PLUGIN_ROOT}/skills/ready/SKILL.md:34`. Shows a goal whose condition is a
  string match on `DOR VERDICT: #<N>` with an explicit list of acceptable statuses and routes.
- **`/verify`**, at `${CLAUDE_PLUGIN_ROOT}/skills/verify/SKILL.md:178`. Same shape, 4 turns, and it accepts
  `PASS-with-caveats` as an exit. Worth copying when a loop has a legitimate partial success.

## What this skill must not do

- **Do not emit a `/goal` for a blocked or misrouted job.** The refusal is the useful output.
- **Do not weaken an exit condition to make it printable.** Say what is missing instead.
- **Do not run the loop.** This skill writes goals. The built-in `/goal` runs them.
- **Do not write to disk.** The loop card is terminal output. If the user wants it kept, they
  will say so.
