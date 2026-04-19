#!/usr/bin/env bash
# Initialize the learnings skill for the current repo.
# Creates .learnings.toml and LEARNINGS.md at the repo root if missing.
# Offers to wire @LEARNINGS.md into the project CLAUDE.md.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "${REPO_ROOT}" ]]; then
  echo "error: not inside a git repository" >&2
  exit 1
fi

PROJECT_NAME=$(basename "${REPO_ROOT}")
TOML_PATH="${REPO_ROOT}/.learnings.toml"
MD_PATH="${REPO_ROOT}/LEARNINGS.md"
CLAUDE_MD_PATH="${REPO_ROOT}/CLAUDE.md"

created_any=0

if [[ -e "${TOML_PATH}" ]]; then
  echo "skip: ${TOML_PATH} already exists"
else
  cat > "${TOML_PATH}" <<EOF
# Configuration for the /learnings skill.
# See ~/.claude/skills/learnings/SKILL.md

enabled = true

# Max entries kept in the Active section before /learnings review warns.
max_active = 100

# Entries older than this (days) get moved to Archived on /learnings review.
archive_after_days = 90
EOF
  echo "created: ${TOML_PATH}"
  created_any=1
fi

if [[ -e "${MD_PATH}" ]]; then
  echo "skip: ${MD_PATH} already exists"
else
  cat > "${MD_PATH}" <<EOF
# Learnings — ${PROJECT_NAME}

Durable project knowledge. One line per entry. Curated by humans and AI via the \`/learnings\` skill.

Legend: ⚖️ decision · 🪤 gotcha · 🧩 pattern · 🔧 tooling
Format: \`YYYY-MM-DD SYMBOL one-line learning (≤100 chars)\`

## Active

## Archived

EOF
  echo "created: ${MD_PATH}"
  created_any=1
fi

echo ""
if [[ -e "${CLAUDE_MD_PATH}" ]]; then
  if grep -qF "@LEARNINGS.md" "${CLAUDE_MD_PATH}" 2>/dev/null; then
    echo "note: ${CLAUDE_MD_PATH} already references @LEARNINGS.md"
  else
    echo "suggestion: append the line below to ${CLAUDE_MD_PATH} so future sessions load learnings automatically:"
    echo ""
    echo "    @LEARNINGS.md"
  fi
else
  echo "note: no CLAUDE.md at repo root. Create one with '@LEARNINGS.md' to auto-load learnings in future sessions."
fi

if [[ ${created_any} -eq 0 ]]; then
  echo ""
  echo "nothing to do — project already initialized"
fi
