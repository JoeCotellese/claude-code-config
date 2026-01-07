#!/bin/bash

# Read JSON input from Claude Code
input=$(cat)

# Extract values from JSON
cwd=$(echo "$input" | jq -r '.workspace.current_dir')

# Get directory (basename for current dir)
dir=$(basename "$cwd")

# Get git branch and status (skip optional locks for safety)
git_info=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" branch --show-current 2>/dev/null || echo "detached")

    # Check for uncommitted changes (skip optional locks)
    if ! git -C "$cwd" diff-index --quiet HEAD -- 2>/dev/null; then
        status="*"
    else
        status=""
    fi

    git_info=" on $(printf '\033[38;2;255;121;198m%s\033[0m' "$branch")$(printf '\033[38;2;255;85;85m%s\033[0m' "$status")"
fi

# Context window percentage (using current_usage for active context)
context_info=""
usage=$(echo "$input" | jq '.context_window.current_usage')
if [ "$usage" != "null" ]; then
    current=$(echo "$usage" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    size=$(echo "$input" | jq '.context_window.context_window_size')
    if [ "$size" != "0" ] && [ "$size" != "null" ]; then
        pct=$((current * 100 / size))
        context_info=" $(printf '\033[38;2;241;250;140m%d%%\033[0m' "$pct")"
    fi
fi

# Build the status line with Starship-inspired colors (simplified)
printf '\033[38;2;80;250;123m%s\033[0m%s%s' \
    "$dir" "$git_info" "$context_info"
