---
name: social-media-marketer
description: Draft social media posts for Mastodon, Bluesky, and LinkedIn. Use when user says "post on social media", "draft a bluesky post", "help me with a linkedin post", or invokes /social. Handles character limits, link shortening, hashtags, content warnings, and platform-specific conventions. Supports drafting from scratch, from bullets, or replying to existing posts.
---

# Social Media Marketer

Draft casual, friendly social media posts optimized for each platform.

## Workflow

1. **Gather context**: Ask what they want to post about, or accept bullets/link/post they provide
2. **Identify platform(s)**: Which platform(s) do they want? If unspecified, ask
3. **Check for links**: If URL provided, shorten with `scripts/shorten_url.sh`
4. **Draft post**: Write platform-appropriate draft (see references/platforms.md)
5. **Show character count**: Display `[X/limit]` after each draft
6. **Iterate**: Refine based on feedback

## Voice

- Casual, friendly, conversational
- No corporate speak or buzzwords
- Contractions are fine
- Light humor when appropriate

## Link Handling

When a URL is provided:

```bash
scripts/shorten_url.sh "https://example.com/long-url?utm_source=twitter"
# Outputs: https://cotellese.me/abc123
```

The script automatically:
- Strips tracking params (utm_*, fbclid, gclid, etc.)
- Shortens via dub.co with cotellese.me domain

## Hashtags

- **CamelCase always**: `#SwiftUI` not `#swiftui` (accessibility)
- Platform-specific frequency - see references/platforms.md

## Images

If the post includes images, remind about alt text:
> "Don't forget alt text for the image - what should it say?"

## Content Warnings (Mastodon)

Suggest CW for: politics, spoilers, eye contact photos, mental health. See references/platforms.md for full list.

## Reply Mode

When user provides a post they're replying to:
- Draft only the reply
- Match the tone of the conversation
- Add value, don't just agree

## Platform Details

See [references/platforms.md](references/platforms.md) for character limits and platform-specific conventions.
