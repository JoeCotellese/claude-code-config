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

    git_info=" on $(printf '\033[35m%s\033[0m' "$branch")$(printf '\033[31m%s\033[0m' "$status")"
fi

# Context heat: absolute size plus one fire per cost band.
#
# The percentage this replaces was a fraction of the 1M window, so the bands
# that carry most of the spend rendered as a reassuring 15-30%. Absolute K maps
# straight onto the thresholds instead. Bands come from measured September
# spend: turns above 150K account for 68% of it, turns above 300K for 24%,
# and a turn at 321K costs ~2.5x the same turn at 87K.
#
# Set STATUSLINE_NO_NERD=1 where a Nerd Font is not installed; the Private Use
# Area glyphs below render as blank boxes in any other font.
context_info=""
usage=$(echo "$input" | jq '.context_window.current_usage')
if [ "$usage" != "null" ]; then
    current=$(echo "$usage" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    if [ -n "$current" ] && [ "$current" != "null" ]; then
        if [ "$current" -ge 300000 ]; then
            heat=2
        elif [ "$current" -ge 150000 ]; then
            heat=1
        else
            heat=0
        fi

        if [ -n "${STATUSLINE_NO_NERD:-}" ]; then
            # Geometric Shapes render in every font; fire does not.
            glyphs=("" "◐" "●")
            icon="${glyphs[$heat]}"
        else
            fire=$(printf '\357\201\255')  # U+F06D nf-fa-fire
            icon=""
            i=0
            while [ "$i" -lt "$heat" ]; do
                icon="$icon$fire"
                i=$((i + 1))
            done
        fi

        # Colour reinforces the count; the count carries the state on its own.
        case "$heat" in
            2) icon=$(printf '\033[31m%s\033[0m ' "$icon") ;;
            1) icon=$(printf '\033[33m%s\033[0m ' "$icon") ;;
            *) icon="" ;;
        esac

        # The number stays neutral so the calm state is visually quiet; the
        # fire owns the one alarm channel rather than colouring both.
        context_info="$(printf ' %s%dK' "$icon" "$((current / 1000))")"
    fi
fi

# Model name
model=$(echo "$input" | jq -r '.model.display_name // empty')
model_info=""
[ -n "$model" ] && model_info=" $(printf '\033[36m%s\033[0m' "$model")"

# Reasoning effort level (payload if present, else last assistant turn in the transcript)
effort=$(echo "$input" | jq -r '[.effort, .model.effort, .reasoning_effort] | map(select(. != null)) | map(if type == "object" then (.level // .effort // empty) else . end) | first // empty')
if [ -z "$effort" ]; then
    transcript=$(echo "$input" | jq -r '.transcript_path // empty')
    if [ -n "$transcript" ] && [ -f "$transcript" ]; then
        effort=$(tail -n 200 "$transcript" | jq -r 'select(.effort != null) | .effort | if type == "object" then (.level // empty) else . end' 2>/dev/null | tail -1)
    fi
fi
effort_info=""
[ -n "$effort" ] && effort_info=" level: $(printf '\033[34m%s\033[0m' "$effort")"

# Build the status line with theme-aware ANSI colors (resolve through the terminal palette)
printf '\033[32m%s\033[0m%s%s%s%s' \
    "$dir" "$git_info" "$model_info" "$context_info" "$effort_info"
