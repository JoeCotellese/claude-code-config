#!/bin/bash
# ABOUTME: Test for the status line's context-heat indicator (absolute K plus repeated fire glyphs).
# ABOUTME: Asserts band thresholds, the dropped percent, the ASCII fallback, and graceful degradation.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINE="$REPO_ROOT/statusline-command.sh"

FIRE=$(printf '\357\201\255')

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n      got: %s\n' "$1" "${2:-}"; fail=1; }

# Build a status line payload with the given cache_read token count.
payload() {
    printf '{"workspace":{"current_dir":"/tmp"},"model":{"display_name":"Opus 5"},"effort":{"level":"high"},"context_window":{"current_usage":{"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":%s},"context_window_size":1000000}}' "$1"
}

# Strip ANSI so assertions read the text, not the color codes.
render() { payload "$1" | bash "$LINE" | sed $'s/\033\\[[0-9;]*m//g'; }

# Count occurrences of the fire glyph in a rendered line.
fires() { printf '%s' "$1" | grep -o "$FIRE" | wc -l | tr -d ' '; }

# --- band thresholds -------------------------------------------------------
out="$(render 87000)"
[ "$(fires "$out")" = "0" ] && pass "87K: no fire" || bad "87K should show no fire" "$out"

out="$(render 149999)"
[ "$(fires "$out")" = "0" ] && pass "149,999: still no fire" || bad "149,999 should show no fire" "$out"

out="$(render 150000)"
[ "$(fires "$out")" = "1" ] && pass "150K: one fire" || bad "150K should show one fire" "$out"

out="$(render 162000)"
[ "$(fires "$out")" = "1" ] && pass "162K: one fire" || bad "162K should show one fire" "$out"

out="$(render 299999)"
[ "$(fires "$out")" = "1" ] && pass "299,999: still one fire" || bad "299,999 should show one fire" "$out"

out="$(render 300000)"
[ "$(fires "$out")" = "2" ] && pass "300K: two fires" || bad "300K should show two fires" "$out"

out="$(render 538000)"
[ "$(fires "$out")" = "2" ] && pass "538K: two fires (top band)" || bad "538K should show two fires" "$out"

# --- the number replaces the percent ---------------------------------------
out="$(render 162000)"
if printf '%s' "$out" | grep -q '162K'; then
    pass "shows absolute context (162K)"
else
    bad "should show absolute context as 162K" "$out"
fi
if printf '%s' "$out" | grep -q '%'; then
    bad "should no longer print a percent" "$out"
else
    pass "no percent in the status line"
fi

# Sub-1K contexts still round to a readable number rather than 0K.
out="$(render 400)"
printf '%s' "$out" | grep -q '0K' && pass "400 tokens renders as 0K" || bad "400 tokens should render as 0K" "$out"

# --- ASCII fallback --------------------------------------------------------
out="$(STATUSLINE_NO_NERD=1 render 162000)"
if printf '%s' "$out" | grep -q '◐' && [ "$(fires "$out")" = "0" ]; then
    pass "STATUSLINE_NO_NERD: half circle replaces one fire"
else
    bad "STATUSLINE_NO_NERD should render a half circle at 162K" "$out"
fi
out="$(STATUSLINE_NO_NERD=1 render 321000)"
if printf '%s' "$out" | grep -q '●'; then
    pass "STATUSLINE_NO_NERD: full circle replaces two fires"
else
    bad "STATUSLINE_NO_NERD should render a full circle at 321K" "$out"
fi

# --- graceful degradation --------------------------------------------------
out="$(printf '{"workspace":{"current_dir":"/tmp"},"model":{"display_name":"Opus 5"}}' | bash "$LINE" | sed $'s/\033\\[[0-9;]*m//g')"
if printf '%s' "$out" | grep -q 'Opus 5' && [ "$(fires "$out")" = "0" ]; then
    pass "missing context_window: renders without a context segment"
else
    bad "missing context_window should still render the rest of the line" "$out"
fi

out="$(printf '{"workspace":{"current_dir":"/tmp"},"context_window":{"current_usage":null}}' | bash "$LINE" | sed $'s/\033\\[[0-9;]*m//g')"
[ -n "$out" ] && pass "null current_usage: still renders" || bad "null current_usage produced nothing" "$out"

printf '\n'
[ "$fail" = "0" ] && printf 'All status line context assertions passed.\n' || printf 'Status line context assertions FAILED.\n'
exit "$fail"
