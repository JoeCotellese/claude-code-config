#!/bin/bash
# ABOUTME: Creates a properly named feature/fix branch from an issue number
# ABOUTME: Usage: create_feature_branch.sh <issue-number> <branch-type> <description>

set -e

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <issue-number> <branch-type> <description>"
    echo "  branch-type: feature, fix, or hotfix"
    echo "  example: $0 123 feature applies-condition-field"
    exit 1
fi

ISSUE_NUM=$1
BRANCH_TYPE=$2
DESCRIPTION=$3

# Validate branch type
if [[ ! "$BRANCH_TYPE" =~ ^(feature|fix|hotfix)$ ]]; then
    echo "Error: branch-type must be 'feature', 'fix', or 'hotfix'"
    exit 1
fi

# Create branch name
BRANCH_NAME="${BRANCH_TYPE}/${ISSUE_NUM}-${DESCRIPTION}"

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Update main branch
echo "📥 Fetching latest from remote..."
git fetch origin

# Get the main branch name (could be 'main' or 'master')
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
echo "📌 Main branch: ${MAIN_BRANCH}"

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo "⚠️  Branch ${BRANCH_NAME} already exists locally"
    read -p "Switch to existing branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout "${BRANCH_NAME}"
        echo "✅ Switched to existing branch: ${BRANCH_NAME}"
    fi
    exit 0
fi

# Ensure we're on main and up to date
git checkout "${MAIN_BRANCH}"
git pull origin "${MAIN_BRANCH}"

# Create and checkout new branch
git checkout -b "${BRANCH_NAME}"

echo "✅ Created and switched to new branch: ${BRANCH_NAME}"
echo "📝 Ready to work on issue #${ISSUE_NUM}"
