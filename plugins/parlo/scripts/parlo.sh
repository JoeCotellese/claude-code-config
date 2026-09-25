#!/bin/bash
# ABOUTME: Profile helper for the parlo plugin: resolves and validates profiles, builds smem cards, speaks phrases.
# ABOUTME: Usage: parlo.sh profile [code] | check <profile> | cards <profile> [smem-export] | say <profile> <text>

set -euo pipefail

PARLO_HOME="${PARLO_HOME:-$HOME/.config/parlo}"

profile() {
    if [ -n "${1:-}" ]; then
        local p="$PARLO_HOME/$1.json"
        [ -f "$p" ] || { echo "No profile $p. Run /parlo:setup $1." >&2; return 1; }
        echo "$p"; return
    fi
    shopt -s nullglob
    local all=() p
    for p in "$PARLO_HOME"/*.json; do [ "${p##*/}" = config.json ] || all+=("$p"); done
    case ${#all[@]} in
        0) echo "No profiles in $PARLO_HOME. Run /parlo:setup <language>." >&2; return 1 ;;
        1) echo "${all[0]}" ;;
        *) echo "Several profiles, pass a code:" >&2; for p in "${all[@]}"; do basename "$p" .json >&2; done; return 1 ;;
    esac
}

check() {
    local errors
    errors=$(jq -r '
        def pair: type == "object" and (.target | type) == "string" and (.english | type) == "string";
        def need(k; ok): if ok then empty else "\(k): missing or wrong type" end;
        need("language"; (.language | type) == "string"),
        need("code"; (.code | type) == "string"),
        need("forvo"; (.forvo | type) == "string"),
        need("level"; (.level | type) == "string"),
        need("smem_deck_id"; (.smem_deck_id | type) == "number" or .smem_deck_id == null),
        need("difficulty"; (.difficulty | type) == "object"),
        need("show_pronunciation"; (.show_pronunciation | type) == "boolean" or .show_pronunciation == null),
        need("sentences (8-10 items, each target/english/parts/swaps)";
            (.sentences | type) == "array" and (.sentences | length) >= 8 and (.sentences | length) <= 10
            and all(.sentences[]; pair and (.parts | type) == "object" and (.swaps | type) == "array" and all(.swaps[]; pair))),
        need("essentials.common"; (.essentials.common | type) == "array" and all(.essentials.common[]; pair)),
        need("essentials.verbs"; (.essentials.verbs | type) == "array"),
        need("essentials.questions_negatives"; (.essentials.questions_negatives | type) == "string"),
        need("essentials.patterns"; (.essentials.patterns | type) == "array")
    ' "$1")
    [ -z "$errors" ] && { echo "ok"; return; }
    echo "$errors" >&2; return 1
}

# Cards run English -> target so review drills producing the language, not recognizing it.
cards() {
    local have='[]'
    [ -n "${2:-}" ] && have=$(jq '[.data.cards[].front]' "$2")
    jq --argjson have "$have" '
        [.sentences[], .sentences[].swaps[], .essentials.common[] | {front: .english, back: .target}]
        | map(select(.front | IN($have[]) | not))
    ' "$1"
}

# Speaks text through ElevenLabs. Audio is saved per voice, model and text, so each phrase is generated once.
say() {
    local profile="$1" text="$2" config="$PARLO_HOME/config.json"
    [ -f "$config" ] || { echo "No $config. Add {\"elevenlabs\": {\"api_key\": \"op://...\", \"voice_id\": \"...\", \"model_id\": \"eleven_multilingual_v2\"}}." >&2; return 1; }
    local code voice model key
    code=$(jq -r '.code' "$profile")
    voice=$(jq -r --slurpfile c "$config" '.voice_id // $c[0].elevenlabs.voice_id' "$profile")
    model=$(jq -r '.elevenlabs.model_id // "eleven_multilingual_v2"' "$config")
    local dir="$PARLO_HOME/audio/$code"
    local file="$dir/$(printf '%s\n%s\n%s' "$voice" "$model" "$text" | shasum | cut -c1-40).mp3"

    if [ ! -s "$file" ]; then
        key=$(jq -r '.elevenlabs.api_key' "$config")
        [[ "$key" == op://* ]] && key=$(op read "$key")
        mkdir -p "$dir"
        local header part
        header=$(mktemp); part="$file.part"
        chmod 600 "$header"
        printf 'xi-api-key: %s\n' "$key" >"$header"
        if ! curl -sS --fail-with-body -X POST "https://api.elevenlabs.io/v1/text-to-speech/$voice" \
            -H "@$header" -H 'Content-Type: application/json' \
            -d "$(jq -nc --arg t "$text" --arg m "$model" --arg l "$code" '{text: $t, model_id: $m, language_code: $l}')" \
            -o "$part"; then
            echo "ElevenLabs request failed: $(cat "$part" 2>/dev/null)" >&2
            rm -f "$header" "$part"; return 1
        fi
        rm -f "$header"; mv "$part" "$file"
    fi
    echo "$file"
    # Speed is applied at playback, so slowing a phrase down never regenerates it.
    local speed="${PARLO_SPEED:-$(jq -r '.speed // 1' "$config")}"
    [ -n "${PARLO_PLAYER-afplay}" ] && "${PARLO_PLAYER-afplay}" -r "$speed" -q 1 "$file"
    return 0
}

cmd="${1:-}"; shift || true
case "$cmd" in
    profile|check|cards|say) "$cmd" "$@" ;;
    *) sed -n '2s/^# ABOUTME: //p' "$0" >&2; exit 2 ;;
esac
