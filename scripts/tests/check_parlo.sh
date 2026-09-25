#!/bin/bash
# ABOUTME: Acceptance test for the parlo language-learning plugin.
# ABOUTME: Checks plugin layout, language-agnostic skills, profile validation, and card generation into a scratch smem DB.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PLUGIN="plugins/parlo"
SKILLS="$PLUGIN/skills"
TOOL="$PLUGIN/scripts/parlo.sh"
EXAMPLE="$PLUGIN/profile.example.json"

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# AC1: plugin is registered and ships the four skills.
jq -e '.name == "parlo"' "$PLUGIN/.claude-plugin/plugin.json" >/dev/null 2>&1 \
    && pass "AC1 plugin.json names parlo" || bad "AC1 plugin.json missing or misnamed"
jq -e '.plugins[] | select(.name == "parlo" and .source == "./plugins/parlo")' .claude-plugin/marketplace.json >/dev/null 2>&1 \
    && pass "AC1 marketplace lists parlo" || bad "AC1 marketplace does not list parlo"
for s in setup drill review explain; do
    [ -f "$SKILLS/$s/SKILL.md" ] && pass "AC1 skill present: $s" || bad "AC1 skill missing: $s"
done

# AC2: no language is hard-coded in the skills; language facts live in the profile.
if [ -d "$SKILLS" ] && ! grep -rniE 'italian|italiano|capisce|cominciamo|basta|niente' "$SKILLS" >/dev/null; then
    pass "AC2 skills carry no hard-coded language"
else
    bad "AC2 skills contain hard-coded language text (or are missing)"
fi

# AC3: the old single-language skills are gone and CLAUDE.md points at parlo.
[ ! -e skills/capisce ] && pass "AC3 skills/capisce removed" || bad "AC3 skills/capisce still present"
[ ! -e skills/learn ]   && pass "AC3 skills/learn removed"   || bad "AC3 skills/learn still present"
if ! grep -q '/capisce' CLAUDE.md && grep -q 'parlo' CLAUDE.md; then
    pass "AC3 CLAUDE.md references parlo, not /capisce"
else
    bad "AC3 CLAUDE.md still references /capisce or lacks parlo"
fi

# AC4: the validator accepts the example profile and rejects a broken one with a message.
if [ -x "$TOOL" ] && "$TOOL" check "$EXAMPLE" >"$TMP/ok.out" 2>&1; then
    pass "AC4 example profile validates"
else
    bad "AC4 example profile rejected (or tool missing)"
fi
jq 'del(.forvo) | .sentences = .sentences[0:3]' "$EXAMPLE" >"$TMP/broken.json" 2>/dev/null
if [ -x "$TOOL" ] && ! "$TOOL" check "$TMP/broken.json" >"$TMP/broken.out" 2>&1 \
    && grep -q 'forvo' "$TMP/broken.out" && grep -q 'sentences' "$TMP/broken.out"; then
    pass "AC4 broken profile rejected, naming each problem"
else
    bad "AC4 broken profile not rejected with named problems"
fi

# AC15: show_pronunciation is an optional boolean, and every skill that shows target phrases honors it.
jq '.show_pronunciation = "yes"' "$EXAMPLE" >"$TMP/pron.json"
if [ -x "$TOOL" ] && ! "$TOOL" check "$TMP/pron.json" 2>&1 | grep -q show_pronunciation; then
    bad "AC15 non-boolean show_pronunciation accepted"
else
    pass "AC15 non-boolean show_pronunciation rejected"
fi
for s in setup drill review; do
    grep -q show_pronunciation "$SKILLS/$s/SKILL.md" 2>/dev/null && pass "AC15 $s honors show_pronunciation" || bad "AC15 $s ignores show_pronunciation"
done

# AC16: drill and review treat a missing accent as a note, except where the accent changes the meaning.
for s in drill review; do
    grep -q 'missing accent' "$SKILLS/$s/SKILL.md" 2>/dev/null && grep -q 'changes the meaning' "$SKILLS/$s/SKILL.md" \
        && pass "AC16 $s tolerates missing accents" || bad "AC16 $s has no accent rule"
done

# AC5: real profiles in the parlo home (if any) also validate.
PARLO_HOME="${PARLO_HOME:-$HOME/.config/parlo}"
for p in "$PARLO_HOME"/*.json; do
    [ -e "$p" ] && [ "${p##*/}" != config.json ] || continue
    "$TOOL" check "$p" >/dev/null 2>&1 && pass "AC5 profile validates: $p" || bad "AC5 profile invalid: $p"
done

# AC6: cards go English -> target, cover sentences, swaps and common words, and skip fronts already in the deck.
if [ -x "$TOOL" ]; then
    "$TOOL" cards "$EXAMPLE" >"$TMP/cards.json" 2>"$TMP/cards.err"
    want=$(jq '[.sentences[], .sentences[].swaps[], .essentials.common[]] | length' "$EXAMPLE")
    got=$(jq 'length' "$TMP/cards.json" 2>/dev/null || echo -1)
    [ "$want" = "$got" ] && pass "AC6 one card per sentence, swap and common word ($got)" || bad "AC6 expected $want cards, got $got"
    first_front=$(jq -r '.sentences[0].english' "$EXAMPLE")
    first_back=$(jq -r '.sentences[0].target' "$EXAMPLE")
    jq -e --arg f "$first_front" --arg b "$first_back" 'any(.[]; .front == $f and .back == $b)' "$TMP/cards.json" >/dev/null 2>&1 \
        && pass "AC6 cards are production direction (English front)" || bad "AC6 sentence card not English -> target"
    [ ! -s "$TMP/cards.err" ] && pass "AC6 card generation is quiet" || bad "AC6 card generation wrote to stderr"

    jq '{status: "ok", data: {cards: [.[0], .[1]]}}' "$TMP/cards.json" >"$TMP/existing.json"
    got2=$("$TOOL" cards "$EXAMPLE" "$TMP/existing.json" | jq 'length')
    [ "$got2" = "$((got - 2))" ] && pass "AC6 existing fronts are skipped" || bad "AC6 dedupe: expected $((got - 2)), got $got2"
else
    bad "AC6 tool missing"
fi

# AC7 (integration): generated cards import into a scratch smem deck and come back out.
if command -v smem >/dev/null && [ -s "$TMP/cards.json" ]; then
    DB="$TMP/smem.db"
    deck=$(smem --db-path "$DB" deck create --name scratch | jq '.data.deck.id')
    smem --db-path "$DB" io import --deck "$deck" --file "$TMP/cards.json" >/dev/null
    n=$(smem --db-path "$DB" card list --deck "$deck" | jq '.data.cards | length')
    [ "$n" = "$got" ] && pass "AC7 smem imported all $n cards" || bad "AC7 smem imported $n of $got cards"
else
    bad "AC7 smem missing or no cards generated"
fi

# AC8: profile resolution. Explicit code wins, a lone profile is picked automatically, two profiles without a code is an error naming both.
if [ -x "$TOOL" ]; then
    H="$TMP/home"; mkdir -p "$H"; cp "$EXAMPLE" "$H/aa.json"
    [ "$(PARLO_HOME="$H" "$TOOL" profile)" = "$H/aa.json" ] && pass "AC8 lone profile resolved" || bad "AC8 lone profile not resolved"
    cp "$EXAMPLE" "$H/bb.json"
    [ "$(PARLO_HOME="$H" "$TOOL" profile bb)" = "$H/bb.json" ] && pass "AC8 explicit code resolved" || bad "AC8 explicit code not resolved"
    if ! PARLO_HOME="$H" "$TOOL" profile >"$TMP/amb.out" 2>&1 && grep -q aa "$TMP/amb.out" && grep -q bb "$TMP/amb.out"; then
        pass "AC8 ambiguous profiles rejected, listing both"
    else
        bad "AC8 ambiguous profiles not rejected with a listing"
    fi
    if ! PARLO_HOME="$TMP/empty" "$TOOL" profile >"$TMP/none.out" 2>&1 && grep -q setup "$TMP/none.out"; then
        pass "AC8 no profile points at setup"
    else
        bad "AC8 missing profile does not point at setup"
    fi
else
    bad "AC8 tool missing"
fi

# Voice: a stub curl and op stand in for ElevenLabs and 1Password. The stub logs each call and writes fake audio to -o.
if [ -x "$TOOL" ]; then
    V="$TMP/voice"; mkdir -p "$V/bin"
    cat >"$V/bin/curl" <<'STUB'
#!/bin/bash
out=""; prev=""
for a in "$@"; do
    [ "$prev" = "-o" ] && out="$a"
    echo "ARG: $a" >>"$CURL_LOG"
    case "$a" in @*) sed 's/^/FILE: /' "${a#@}" >>"$CURL_LOG"; echo >>"$CURL_LOG" ;; esac
    prev="$a"
done
echo "--- end call" >>"$CURL_LOG"
[ -n "${CURL_FAIL:-}" ] && exit 22
printf 'ID3fake' >"$out"
STUB
    printf '#!/bin/bash\necho "key-from-1password"\n' >"$V/bin/op"
    chmod +x "$V/bin/curl" "$V/bin/op"
    VH="$V/home"; mkdir -p "$VH"; cp "$EXAMPLE" "$VH/it.json"
    say() { PATH="$V/bin:$PATH" PARLO_HOME="$VH" PARLO_PLAYER=true CURL_LOG="$V/curl.log" "$TOOL" say "$VH/it.json" "$@"; }

    # AC9: config.json lives beside profiles but is never picked as one.
    printf '{"elevenlabs": {"api_key": "op://Private/ElevenLabs/credential", "voice_id": "cfgvoice", "model_id": "eleven_multilingual_v2"}}' >"$VH/config.json"
    [ "$(PARLO_HOME="$VH" "$TOOL" profile)" = "$VH/it.json" ] && pass "AC9 config.json is not a profile" || bad "AC9 config.json treated as a profile"

    # AC10: first say calls the API once with config settings, saves audio, prints its path; second say reuses it.
    : >"$V/curl.log"
    p1=$(say "Vorrei un caffè." 2>"$V/say.err")
    calls=$(grep -c -- '--- end call' "$V/curl.log")
    [ "$calls" = 1 ] && [ -s "$p1" ] && pass "AC10 first say generates and saves audio" || bad "AC10 first say: calls=$calls path=$p1"
    grep -q '/v1/text-to-speech/cfgvoice' "$V/curl.log" && pass "AC10 uses voice_id from config" || bad "AC10 voice_id from config not used"
    grep -q 'xi-api-key: key-from-1password' "$V/curl.log" && pass "AC10 op:// api_key resolved through op" || bad "AC10 op:// api_key not resolved"
    grep -q '"language_code":"it"' "$V/curl.log" && grep -q '"model_id":"eleven_multilingual_v2"' "$V/curl.log" \
        && pass "AC10 sends language_code and model_id" || bad "AC10 language_code/model_id missing from body"
    if grep -q '^ARG: .*key-from-1password' "$V/curl.log"; then
        bad "AC10 api key visible as a curl argument"
    else
        pass "AC10 api key passed by header file, not argument"
    fi
    p2=$(say "Vorrei un caffè.")
    calls=$(grep -c -- '--- end call' "$V/curl.log")
    [ "$calls" = 1 ] && [ "$p1" = "$p2" ] && pass "AC10 second say reuses saved audio" || bad "AC10 second say called API again (calls=$calls)"
    [ ! -s "$V/say.err" ] && pass "AC10 say is quiet on success" || bad "AC10 say wrote to stderr"

    # AC11: profile voice_id overrides config and gets its own audio file.
    jq '.voice_id = "profilevoice"' "$VH/it.json" >"$V/p.json" && mv "$V/p.json" "$VH/it.json"
    p3=$(say "Vorrei un caffè.")
    grep -q '/v1/text-to-speech/profilevoice' "$V/curl.log" && [ "$p3" != "$p1" ] \
        && pass "AC11 profile voice_id overrides config" || bad "AC11 profile voice_id not used"

    # AC14: playback speed comes from config, PARLO_SPEED overrides it, and neither triggers a new API call.
    printf '#!/bin/bash\necho "$@" >>"%s"\n' "$V/player.log" >"$V/bin/player"; chmod +x "$V/bin/player"
    calls_before=$(grep -c -- '--- end call' "$V/curl.log")
    jq '.speed = 0.8' "$VH/config.json" >"$V/c.json" && mv "$V/c.json" "$VH/config.json"
    : >"$V/player.log"
    PATH="$V/bin:$PATH" PARLO_HOME="$VH" PARLO_PLAYER=player CURL_LOG="$V/curl.log" "$TOOL" say "$VH/it.json" "Vorrei un caffè." >/dev/null
    PATH="$V/bin:$PATH" PARLO_HOME="$VH" PARLO_PLAYER=player PARLO_SPEED=0.6 CURL_LOG="$V/curl.log" "$TOOL" say "$VH/it.json" "Vorrei un caffè." >/dev/null
    grep -q -- '-r 0.8' <(sed -n 1p "$V/player.log") && pass "AC14 config speed passed to player" || bad "AC14 config speed not used: $(sed -n 1p "$V/player.log")"
    grep -q -- '-r 0.6' <(sed -n 2p "$V/player.log") && pass "AC14 PARLO_SPEED overrides config" || bad "AC14 PARLO_SPEED ignored: $(sed -n 2p "$V/player.log")"
    [ "$(grep -c -- '--- end call' "$V/curl.log")" = "$calls_before" ] && pass "AC14 speed change reuses saved audio" || bad "AC14 speed change called the API"

    # AC12: a failed API call leaves nothing cached and says why.
    n_before=$(find "$VH/audio" -type f 2>/dev/null | wc -l)
    if ! CURL_FAIL=1 say "Dov'è il bagno?" >"$V/fail.out" 2>"$V/fail.err" && [ ! -s "$V/fail.out" ] \
        && [ -s "$V/fail.err" ] && [ "$(find "$VH/audio" -type f 2>/dev/null | wc -l)" = "$n_before" ]; then
        pass "AC12 failed call caches nothing"
    else
        bad "AC12 failed call left output or partial audio"
    fi

    # AC13: missing config says where to put it.
    rm "$VH/config.json"
    if ! say "Grazie." >/dev/null 2>"$V/nocfg.err" && grep -q 'config.json' "$V/nocfg.err"; then
        pass "AC13 missing config points at config.json"
    else
        bad "AC13 missing config not reported"
    fi
else
    bad "AC9-13 tool missing"
fi

exit $fail
