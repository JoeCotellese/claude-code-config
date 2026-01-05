#!/bin/bash
# ABOUTME: Pre-commit hook that blocks commits to main/master branches
# ABOUTME: Install using setup_git_hooks.sh

# Get current branch name
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)

# Block commits to main or master
if [[ "$BRANCH" == "main" ]] || [[ "$BRANCH" == "master" ]]; then
    echo "❌ ERROR: Direct commits to '${BRANCH}' branch are not allowed!"
    echo ""
    echo "Please create a feature branch instead:"
    echo "  git checkout -b feature/<issue-number>-<description>"
    echo ""
    echo "Or use the helper script:"
    echo "  bash scripts/create_feature_branch.sh <issue-number> feature <description>"
    echo ""
    echo "If you absolutely must commit to ${BRANCH} (dangerous!):"
    echo "  git commit --no-verify"
    exit 1
fi

echo "✅ Committing to branch: ${BRANCH}"
