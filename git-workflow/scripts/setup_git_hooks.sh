#!/bin/bash
# ABOUTME: Installs pre-commit hook to block commits to main/master
# ABOUTME: Run this script once per repository to set up git hooks

set -e

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

GIT_DIR=$(git rev-parse --git-dir)
HOOK_PATH="${GIT_DIR}/hooks/pre-commit"

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_HOOK="${SCRIPT_DIR}/pre_commit_hook.sh"

# Check if source hook exists
if [ ! -f "${SOURCE_HOOK}" ]; then
    echo "❌ Error: Cannot find pre_commit_hook.sh at ${SOURCE_HOOK}"
    exit 1
fi

# Backup existing hook if present
if [ -f "${HOOK_PATH}" ]; then
    echo "⚠️  Existing pre-commit hook found"
    BACKUP_PATH="${HOOK_PATH}.backup-$(date +%Y%m%d-%H%M%S)"
    mv "${HOOK_PATH}" "${BACKUP_PATH}"
    echo "📦 Backed up to: ${BACKUP_PATH}"
fi

# Copy hook and make executable
cp "${SOURCE_HOOK}" "${HOOK_PATH}"
chmod +x "${HOOK_PATH}"

echo "✅ Pre-commit hook installed successfully!"
echo "📝 The hook will block direct commits to main/master branches"
echo ""
echo "To bypass the hook in emergencies (not recommended):"
echo "  git commit --no-verify"
