---
name: retro
max_words: 1900
effort: medium
description: "Loop repair after a failure. Invoke with `/retro` or when the user says 'why did that get through', 'retro this', 'fix the gate', 'that should have been caught'. Runs after a DoR failure, a blocking committee finding, or a failed Definition of Done: names the gate that should have caught it, amends the upstream skill or standard so it would, and records the entry. Without this the development loop is just a longer straight line."
---

# Loop Repair

The reverse edge that makes the loop worth having. Every other phase moves an issue forward.
This one moves the *process* forward, by asking what let the defect through and fixing that
instead of only fixing the defect.

```
/spec  →  /ready  →  /ui-design  →  /implement  →  /verify  →  /submit
   ▲         ▲            ▲                            │
   └─────────┴────────────┴──────── /retro ◄───────────┘
              amends the gate that missed it
```

Run it when:

- `/ready` prints a `DOR VERDICT` with `status=FAIL` — the specification phase shipped an
  issue that was not ready.
- A `/ui-design` or `/submit` committee returns a blocking finding — a review caught something
  the builder should have been told about up front.
- `/verify` prints a `DOD VERDICT` with `route=/retro` — the acceptance test and the
  acceptance criteria disagree, so the gate itself is wrong.
- A defect reaches production. The gate that should have caught it is further back, but the
  procedure is the same.

## Usage

```
/retro                      # uses the failure in the current conversation
/retro #<issue_number>      # pulls the verdict lines and comments from the issue
```

Human gated throughout. This skill proposes an amendment to a standard you rely on across
every project; it does not land one on its own.

## The rule that keeps this useful

**Amend only what would recur.** A retro that files an amendment for every failure buries the
rubric in special cases until nobody reads it, which is the same outcome as having no rubric.

Ask: would this same failure happen again on a different issue, in a different project, with a
different feature? If yes, amend. If no, record the entry and stop. A one-off gets a line in
`LEARNINGS.md` and nothing more, and that is a complete, successful retro.

## Workflow

### Step 1 — State the failure in one line

Quote the evidence, do not summarize it. The `DOR VERDICT` line, the blocking finding verbatim,
the failing `success_criteria` entry. A retro built on a paraphrase fixes a paraphrase.

### Step 2 — Name the gate that should have caught it

Every failure escaped a specific gate. Name the one, not the list:

- Acceptance criteria too vague to test → **R2 at `/ready`**, and behind it the AC wording rule
  in `/spec`.
- Element had no identifier so the test could not address it → **R3 at `/ready`**.
- Design never existed and got discovered at implementation time → **R4 at `/ready`**.
- Issue was three features → **R6 at `/ready`**, and behind it the sizing step in `/spec`.
- Acceptance test asserts something the ACs never said → **R7 at `/ready`**.
- Test passed but the feature is broken → the acceptance test had a **test-only backdoor**, or
  a criterion had **no channel** observing it. R7 and R2 respectively.
- Reviewer found a class of problem the builder had no way to anticipate → the **standard is
  not written down**, so no gate could have caught it. This routes to a docs amendment rather
  than a rubric one.

If you cannot name a gate, say so. "Nothing in the process could have caught this" is a real
and acceptable answer, and it stops here with a `LEARNINGS.md` entry.

### Step 3 — Classify the cause

One of these. The classification picks the fix.

- **Missing criterion** — the rubric never asked. Fix: add a criterion.
- **Weak criterion** — the rubric asked, and a compliant answer still let the defect through.
  Fix: sharpen the wording, usually by adding the observable form or a counter-example. This
  is the most common and the most valuable.
- **Skipped phase** — the rubric was fine and nobody ran it. Fix: nothing in the rubric. Say
  which phase was skipped and why, because "we were in a hurry" repeated four times is a
  finding about the process's cost, not about its content.
- **Undocumented standard** — the expectation was real but lived only in someone's head. Fix:
  write it into the platform docs under `~/.claude/docs/` or the project's `CLAUDE.md`.
- **One-off** — genuinely unrepeatable. Fix: record only.

### Step 4 — Write the smallest amendment that would have caught it

The test for a good amendment: **replay the failure against the amended text.** If the issue
that failed would now be caught by the new wording, it works. If you have to squint, it does
not, and you are adding words that will be skimmed past next time.

Prefer, in order:

1. A **counter-example** added to an existing criterion. Rubrics fail on ambiguity far more
   often than on omission, and one concrete FAIL example fixes more ambiguity than a paragraph
   of explanation.
2. A **sharpened existing criterion**.
3. A **new criterion**, only when nothing existing covers the ground.

Never delete or weaken a criterion to resolve a retro. If a criterion seems to be causing more
friction than it catches, that is a conversation with the user, not an edit.

### Step 5 — Decide the amendment's scope, then send it there

Two destinations, and the question that picks between them is the one Step 4's rule already
asks: **would this failure recur on a different issue, in a different project?**

- **This project only** → write the amendment to `.dev-jawn/<skill>.md` in the repo you are
  working in. This is the default when you are unsure.
- **Anywhere** → file it as an issue against the repository that ships the plugin.

**Never edit the plugin source.** Not the installed copy under
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, which the next version bump
replaces wholesale and silently destroys anything written there. And not a local clone either,
even when you are the maintainer and it is sitting right there. The maintainer path and the
end-user path being the same path is the point.

#### Resolving the upstream repository

`gh issue create --repo` needs an `owner/repo`, and no single file carries one. Three steps:

1. The skill file's own path names its plugin: `plugins/<plugin>/skills/<skill>/SKILL.md`.
2. `~/.claude/plugins/installed_plugins.json` keys plugins as `<plugin>@<marketplace>`. Read
   the marketplace name out of that key.
3. Look the marketplace up in `~/.claude/plugins/known_marketplaces.json` and derive
   `owner/repo` from its `.source.source`:
   - `github` — `.source.repo` is already `owner/repo`. Use it.
   - `git` — parse `owner/repo` out of `.source.url`.
   - `directory` — `git -C <.source.path> remote get-url origin`, then parse.

Then `gh issue create --repo <owner/repo>`, with the failure quoted, the gate named, and the
amendment written out as the proposed wording.

**If any step fails to resolve** — a marketplace not in the file, a `directory` source with no
origin remote, no `gh` on the machine — do not guess and do not fall back to editing. Print
the amendment in the transcript and end the retro with `dest=unresolved`, so the lesson is at
least visible even though it could not be filed.

#### The intake budget

Each phase skill declares a `max_words:` ceiling in its frontmatter, and
`scripts/tests/check_dev_jawn.sh` asserts it, so the limit is a test rather than an intention.
An amendment that would push a skill past its ceiling does not simply land. It must **replace**
a weaker counter-example on the same criterion, stay **local** only, or trigger a
**consolidation** of that section first. State which of the three you chose in the issue you
file.

#### Local amendments are inert for now

Nothing reads `.dev-jawn/` yet; issue **#64** is what gives the gates that ability. Until it
lands, a repo-local amendment is a record and not a constraint, and the retro must say so
rather than implying the gate now catches it.

### Step 6 — Record the entry

Append to the project's `LEARNINGS.md` using the `learnings` skill, which owns the format and
the deduplication. One line, dated, symbol-prefixed. This happens for every retro including
one-offs and including "no gate could have caught it".

### Step 7 — Print the retro line

On its own line, so it is greppable and a goal evaluator can read it:

```
RETRO: #347  gate=R2   cause=weak-criterion  scope=local     dest=.dev-jawn/ready.md
RETRO: #347  gate=R2   cause=weak-criterion  scope=upstream  dest=https://github.com/o/r/issues/12
RETRO: #347  gate=none cause=one-off         scope=none      dest=LEARNINGS.md
```

- `gate` — the criterion or phase that should have caught it, or `none`.
- `cause` — one of `missing-criterion`, `weak-criterion`, `skipped-phase`,
  `undocumented-standard`, `one-off`.
- `scope` — `local`, `upstream`, or `none`.
- `dest` — the repo-local file, the filed issue's URL, `LEARNINGS.md` for a one-off, or
  `unresolved` when the upstream repository could not be resolved.

## Success Condition

The failure is quoted, a gate is named or explicitly ruled out, a `LEARNINGS.md` entry exists,
and the amendment reached its destination: a repo-local file, an issue filed upstream, or a
transcript entry when neither applied. A retro that produces analysis and no artifact did not
happen.

## What this skill must not do

- **Do not fix the issue.** That is `/implement`'s job and it is probably already done. This
  phase touches the process.
- **Do not amend on a single data point when the cause is `skipped-phase`.** The rubric is not
  the problem.
- **Do not weaken a gate to stop it failing.** Failing gates are the gates working.
- **Do not batch retros.** Four failures analyzed together produce one vague amendment that
  addresses none of them.

## Dependencies

- `learnings` skill for the `LEARNINGS.md` format
- `glab` or `gh` when pulling the verdict from an issue
- `gh` for filing an upstream issue, and read access to `~/.claude/plugins/*.json`

## Next Phase

Back to whatever the original failure's route said. `/retro` is a side trip: it does not
advance the issue, and the issue still needs `/spec`, `/ready`, or `/implement` to move.
