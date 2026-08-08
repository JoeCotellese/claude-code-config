#!/bin/bash
# ABOUTME: Installs git hooks for branch protection and commit message validation
# ABOUTME: Run this script once per repository to set up git hooks

set -e

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

GIT_DIR=$(git rev-parse --git-dir)
HOOKS_DIR="${GIT_DIR}/hooks"

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to install a hook
install_hook() {
    local HOOK_NAME="$1"
    local SOURCE_FILE="$2"
    local DESCRIPTION="$3"

    local HOOK_PATH="${HOOKS_DIR}/${HOOK_NAME}"
    local SOURCE_HOOK="${SCRIPT_DIR}/${SOURCE_FILE}"

    if [ ! -f "${SOURCE_HOOK}" ]; then
        echo "⚠️  Warning: Cannot find ${SOURCE_FILE} at ${SOURCE_HOOK}"
        return 1
    fi

    # Backup existing hook if present
    if [ -f "${HOOK_PATH}" ]; then
        echo "⚠️  Existing ${HOOK_NAME} hook found"
        BACKUP_PATH="${HOOK_PATH}.backup-$(date +%Y%m%d-%H%M%S)"
        mv "${HOOK_PATH}" "${BACKUP_PATH}"
        echo "   📦 Backed up to: ${BACKUP_PATH}"
    fi

    # Copy hook and make executable
    cp "${SOURCE_HOOK}" "${HOOK_PATH}"
    chmod +x "${HOOK_PATH}"

    echo "✅ ${HOOK_NAME} hook installed: ${DESCRIPTION}"
}

echo "Installing git hooks..."
echo ""

# Install pre-commit hook (blocks commits to main/master)
install_hook "pre-commit" "pre_commit_hook.sh" "Blocks direct commits to main/master"

# Install commit-msg hook (validates commit message format)
install_hook "commit-msg" "commit_msg_hook.sh" "Enforces commit message format"

echo ""
echo "📝 Hooks installed:"
echo "   - pre-commit: Blocks commits to main/master branches"
echo "   - commit-msg: Validates type prefix, issue reference, length"
echo ""
echo "To bypass hooks in emergencies (not recommended):"
echo "  git commit --no-verify"
