#!/bin/bash
# ABOUTME: Shortens URLs using dub.co API with cotellese.me domain.
# ABOUTME: Strips tracking parameters before shortening.

set -euo pipefail

URL="$1"

if [[ -z "$URL" ]]; then
  echo "Usage: shorten_url.sh <url>" >&2
  exit 1
fi

if [[ -z "${DUB_API_KEY:-}" ]]; then
  echo "Error: DUB_API_KEY environment variable not set" >&2
  exit 1
fi

# Strip common tracking parameters
CLEAN_URL=$(echo "$URL" | sed -E '
  s/[?&](utm_[a-z_]+|fbclid|gclid|mc_[a-z_]+|_ga|_gl|ref|source|campaign|medium|content|term|hsCtaTracking|hsa_[a-z]+|msclkid|igshid|si|pp|s)=[^&]*//g
  s/[?&]$//
  s/\?&/?/
')

# Call dub.co API
RESPONSE=$(curl -s -X POST "https://api.dub.co/links" \
  -H "Authorization: Bearer $DUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$CLEAN_URL\", \"domain\": \"cotellese.me\"}")

# Extract short link from response
SHORT_URL=$(echo "$RESPONSE" | jq -r '.shortLink // empty')

if [[ -z "$SHORT_URL" ]]; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error.message // .message // "Unknown error"')
  echo "Error: $ERROR" >&2
  exit 1
fi

echo "$SHORT_URL"
