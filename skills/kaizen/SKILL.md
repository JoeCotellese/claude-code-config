# Kaizen - Continuous Improvement Skill

## Description

Kaizen (改善, "change for better") analyzes the current session to identify inefficiencies, tool misuse, missing documentation, and contradictory instructions. It suggests concrete improvements to CLAUDE.md files and skills, then offers to implement the changes.

It also has a **system-prompt redundancy audit** mode (`/kaizen prompts`) that ignores the session and instead diffs the user's durable config against Claude Code's own system prompts, surfacing rules the harness now ships itself.

## Invocation

- Session review: `/kaizen` or "review this session for improvements"
- System-prompt audit: `/kaizen prompts` or "audit my config against the system prompts"

## Analysis Categories

### 1. Tool Misuse Detection

Look for patterns where Claude used suboptimal tools:

- **File operations via Bash**: Using `cat`, `head`, `tail`, `sed`, `awk`, `echo >` instead of Read/Edit/Write tools
- **Search via Bash**: Using `grep`, `rg`, `find`, `fd` commands instead of Grep/Glob tools
- **Missing parallelization**: Sequential tool calls that could have been parallel
- **Wrong agent type**: Using general Task agent when a specialized agent (Explore, Plan) would be better
- **Excessive searching**: Multiple search rounds when the target could be documented

### 2. Missing Documentation

Identify information gaps that caused friction:

- Questions Claude had to ask that could be pre-answered in CLAUDE.md
- API endpoints, commands, or patterns Claude had to discover through exploration
- Architecture or conventions that required extensive codebase searching
- External service configurations not documented
- Common workflows that should be scripted or documented

### 3. Instruction Contradictions

Flag conflicting guidance between or within configuration files:

- **Global vs Project CLAUDE.md**: Different rules for the same scenario
- **Within-file conflicts**: Contradictory statements in the same document
- **Skill vs CLAUDE.md conflicts**: Skill instructions that contradict main config
- **Implicit contradictions**: Rules that create impossible situations when combined
- **Ambiguous instructions**: Guidelines that could be interpreted multiple ways

### 4. Inefficiency Patterns

Spot workflow problems:

- Repeated failed attempts before success
- Back-and-forth clarification that indicates unclear requirements
- Rework due to misunderstood context
- Overly complex solutions when simpler approaches exist
- Missing skills that would automate repetitive patterns

### 5. Skill Gaps

Identify opportunities for new or enhanced skills:

- Repetitive multi-step workflows that could be encapsulated
- Domain-specific patterns that warrant dedicated skills
- Existing skills that are missing useful functionality
- Cross-skill coordination opportunities

## Mode: System-Prompt Redundancy Audit

Separate from the session review above. Triggered by `/kaizen prompts` or "audit my config against the system prompts". This mode does NOT analyze the current session — it diffs the user's durable config against Claude Code's own system prompts to find rules the harness now ships itself.

**Why:** As Claude Code evolves, behavior that once had to live in CLAUDE.md (comment style, action safety, task hygiene) gets baked into the system prompt. Those CLAUDE.md rules become redundant; some (like an ABOUTME-header rule) become conflicts the user is overriding on purpose. This mode surfaces both.

**Source of truth:** `Piebald-AI/claude-code-system-prompts` — system prompts extracted from Claude Code's compiled source, one markdown file per component, each tagged with the `ccVersion` it reflects.

### Steps

1. Shallow-clone the repo to a temp dir (discard when done — no vendored copy to keep in sync):
   `git clone --depth 1 https://github.com/Piebald-AI/claude-code-system-prompts.git`
2. Read the version it reflects (README / `ccVersion` headers) and compare to the running Claude Code (`claude --version`). Warn if the repo is behind or ahead — the diff is only as current as the repo.
3. Diff the user's durable config against the behavioral cluster of `system-prompts/system-prompt-*.md` (tone/style, comments, doing-tasks, action-safety, editing). Targets:
   - `~/.claude/CLAUDE.md` (resolve the symlink to the real file in this repo before editing)
   - user skills under `skills/`
4. Classify every overlapping rule:
   - **Redundant** — the harness now states it; the CLAUDE.md line can be trimmed or deleted.
   - **Conflicting** — the config deliberately overrides the harness (e.g. the ABOUTME header vs the harness's "don't explain WHAT the code does"). Keep it, but flag it so the override stays conscious.
   - **Keep** — personal preference or project workflow with no harness equivalent (anti-sycophancy tone, git routing, tooling choices). Leave untouched.
5. Report using the Output Format below, then offer to apply the trims.

### Notes

- Only the behavioral system-prompt files overlap durable config. Skip tool descriptions, agent prompts, and mode-specific fragments (plan mode, coordinator, etc.) unless the user asks for a full sweep.
- Don't strip a rule just because the harness echoes it when the CLAUDE.md version is deliberately stronger (e.g. "NEVER commit to main" vs the harness's softer "branch first"). Note the overlap; leave the stronger rule.
- Low-frequency chore — run it after a Claude Code upgrade, not every session.

## Output Format

Present findings in this structure:

```
## Kaizen Session Review

### Issues Found

#### Tool Misuse
- [Issue description with specific example from session]
- Recommendation: [Concrete fix]

#### Missing Documentation
- [What was missing and how it caused friction]
- Recommendation: [What to add and where]

#### Contradictions
- [Conflicting instructions with file locations]
- Recommendation: [How to resolve]

#### Inefficiencies
- [Pattern observed]
- Recommendation: [Improvement]

#### Skill Gaps
- [Opportunity identified]
- Recommendation: [New skill or enhancement]

### Proposed Changes

1. **[File path]**: [Summary of change]
2. **[New skill name]**: [What it would do]
...

Would you like me to implement these changes?
```

## Workflow

1. **Review the session**: Analyze the full conversation for issues in each category
2. **Prioritize findings**: Focus on high-impact, actionable improvements
3. **Present findings**: Output structured report to console
4. **Offer implementation**: Ask user which changes to make
5. **Apply changes**: Edit CLAUDE.md files, create/update skills as approved

## Analysis Checklist

When reviewing the session, systematically check:

- [ ] Were Read/Edit/Write tools used instead of Bash for file operations?
- [ ] Were Grep/Glob tools used instead of shell commands for searching?
- [ ] Were independent tool calls made in parallel?
- [ ] Was the Explore agent used for open-ended codebase questions?
- [ ] Did Claude have to ask clarifying questions that could be pre-documented?
- [ ] Did Claude search extensively for information that should be in CLAUDE.md?
- [ ] Are there conflicting instructions between global and project configs?
- [ ] Are there ambiguous guidelines that caused misinterpretation?
- [ ] Were there failed attempts that better docs would have prevented?
- [ ] Is there a repetitive pattern that warrants a new skill?

## Examples

### Example: Tool Misuse Finding

```
#### Tool Misuse
- Used `cat package.json | jq '.scripts'` via Bash instead of Read tool
- Line 47 of session: Should have used Read tool then parsed in response
- Recommendation: Add reminder to CLAUDE.md: "Use Read tool for JSON files, parse content in response rather than piping through jq"
```

### Example: Missing Documentation Finding

```
#### Missing Documentation
- Spent 3 tool calls discovering the test command is `yarn test:unit` not `yarn test`
- This is a project-specific convention not documented anywhere
- Recommendation: Add to project CLAUDE.md under Common Commands:
  ```
  ### Testing
  yarn test:unit    # Run unit tests (NOT yarn test)
  yarn test:e2e     # Run e2e tests
  ```
```

### Example: Contradiction Finding

```
#### Contradictions
- Global CLAUDE.md says "Always use TypeScript strict mode"
- Project CLAUDE.md says "Match existing code style" but project uses loose TS
- Creates confusion about which rule takes precedence
- Recommendation: Add to project CLAUDE.md: "Project uses loose TypeScript (override global strict mode preference)"
```

## Notes

- Focus on actionable improvements, not theoretical perfection
- Prioritize changes that prevent future friction over minor optimizations
- Be specific with file paths and line references when suggesting changes
- Consider the cost/benefit of adding documentation vs. one-time friction
- Don't suggest changes for edge cases unlikely to recur
