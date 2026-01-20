#!/bin/bash
# ABOUTME: Detects whether repository uses GitHub or GitLab
# ABOUTME: Returns "github", "gitlab", or "unknown"

set -e

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "unknown"
    exit 0
fi

# Get remote URL
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "unknown"
    exit 0
fi

# Check for GitHub
if [[ "$REMOTE_URL" == *"github.com"* ]]; then
    echo "github"
    exit 0
fi

# Check for GitLab
if [[ "$REMOTE_URL" == *"gitlab.com"* ]] || [[ "$REMOTE_URL" == *"gitlab"* ]]; then
    echo "gitlab"
    exit 0
fi

echo "unknown"
