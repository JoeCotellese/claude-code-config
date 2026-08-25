#!/usr/bin/env bash
# ABOUTME: UserPromptSubmit hook that injects the dev-jawn workflow policy into context each turn.
# ABOUTME: Carries the rules formerly in CLAUDE.md's "Git Workflow (CRITICAL)" section; toggles with the plugin.

# Injected unconditionally on every prompt, mirroring the always-on nature of
# the CLAUDE.md section it replaces. Emits its text as additionalContext so the
# policy travels with the plugin: disable dev-jawn and this hook stops firing,
# so the rules leave context with the skills. ${CLAUDE_PLUGIN_ROOT} is exported
# into this process, so the WORKFLOW.md pointer resolves to a concrete path.

set -euo pipefail

# Quiet mode: a repo that wants the phase skills available but not the every-prompt nudge marks
# itself by putting a `dev-jawn: quiet` sentinel in its CLAUDE.md (or .claude/CLAUDE.md). When the
# marker is present we inject nothing and exit — the skills stay loaded (unlike disabling the
# plugin), so /spec, /ready, etc. still work when invoked by hand. See plugins/dev-jawn/README.md.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
for marker_file in "$PROJECT_DIR/CLAUDE.md" "$PROJECT_DIR/.claude/CLAUDE.md"; do
    if [ -f "$marker_file" ] && grep -qiE 'dev-jawn:[[:space:]]*quiet' "$marker_file"; then
        exit 0
    fi
done

WORKFLOW="${CLAUDE_PLUGIN_ROOT:-.}/skills/WORKFLOW.md"

read -r -d '' POLICY <<EOF || true
# Git Workflow (CRITICAL) — provided by the dev-jawn plugin
- NEVER commit directly to main/master branch. Always create a feature branch first.
- When the user says "implement", "work on issue", "fix", or mentions an issue number, invoke a phase skill IMMEDIATELY, before writing any code. Pick by the state of the work: nothing filed yet -> /spec; a filed issue that has not passed the Definition of Ready -> /ready #N, which audits, repairs what it can, and routes onward itself; an issue already carrying a passing DOR VERDICT and its committed acceptance test -> /implement #N; code already written -> /submit.
- Do NOT skip /ready because the issue looks complete. Judging whether it is complete is the gate's job, not yours. Skip it only when told to.
- Those are phases of a loop: /spec -> /ready -> /ui-design -> /implement -> /verify -> /submit, with /retro as the reverse edge when something gets through a gate it should not have. Read ${WORKFLOW} when entering the loop at any phase or when a phase routes work backwards. It holds the Definition of Ready, the Definition of Done, and the seven loops with their exit conditions.
- Branch naming: <prefix>/<issue>-<desc>. See ~/.claude/docs/source-control.md for the full prefix set (feature, fix, hotfix, chore, docs, test, refactor).
- All changes must go through PRs for review.
EOF

jq -n --arg ctx "$POLICY" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $ctx}}'
