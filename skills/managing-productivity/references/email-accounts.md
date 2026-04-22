# Email Accounts (rusty-apple-mail MCP)

Static mapping of `account_id` UUIDs (returned by `mcp__rusty-apple-mail__list_accounts`) to their email addresses. Pass these as the `account` parameter to `search_messages`.

| account_id | Email | Notes |
|---|---|---|
| `imap://46C99396-8C53-4C35-8A1A-071548F6E6D2` | joe@cotellese.net | Non-Gmail IMAP (legacy/Fastmail-style). Has `Sent Messages`, `Archives/2023-2024`. |
| `imap://4EE80155-AD91-4EE2-9632-3EA58C5F20F4` | joe@cotellese.net | **Primary Gmail/Workspace.** Has `WavelyDX`, `Lisa Cotellese`, `mailfiler/*`, `n8n/*` automation folders. Default for personal email. |
| `imap://660D6AF8-E0A0-4D27-BD63-E184D3CE5C6F` | joe@appjawn.com | Gmail w/ SaneBox (`@SaneReceipts`, `@SaneTomorrow`), `dmarc-reports`, `support`. |
| `imap://6A2D79A3-3393-46C8-B770-400E21AEFB48` | joe.cotellese@nextgres.com | Gmail w/ Mixmax (sales outbound — `Mixmax: Marketing/Cold emails`). |
| `imap://FD1641D9-9B7C-4F71-B842-BA8C2F1684CA` | joe@eye.guide | Gmail (small mailbox). |
| `local://4F550B18-69BF-4058-B9C2-683FCD1DFB09` | (local "On My Mac") | Recovered Cotellese.net messages only. Not for active use. |

## Default selection

When the user references "my email" or "email" without qualification, use **`imap://4EE80155-AD91-4EE2-9632-3EA58C5F20F4`** (primary Gmail for joe@cotellese.net).

## Per-context routing

| Context cue | Account |
|---|---|
| Personal, "my inbox", calendar invites | `4EE80155-…` (joe@cotellese.net Gmail) |
| AppJawn, receipts, app/business admin | `660D6AF8-…` (joe@appjawn.com) |
| Nextgres, sales outreach, prospects | `6A2D79A3-…` (joe.cotellese@nextgres.com) |
| Eye.guide / FDA review correspondence | `FD1641D9-…` (joe@eye.guide) |

## Maintenance

If `list_accounts` returns an `account_id` not listed here, a new account was added to Apple Mail. Identify it by calling `get_message` with `include_recipients=true` on a recent inbox message and reading the `to` field, then update this table.
