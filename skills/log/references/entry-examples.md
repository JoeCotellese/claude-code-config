# DEVLOG Entry Examples

Reference examples for different types of development log entries.

## Bug Investigation

```markdown
## Jan 15, 2026 10:30

- **Problem**: Login form submits but user not authenticated
- **Tried**: Checked network tab - POST succeeds, returns 200 with token
- **Found**: Token stored in localStorage but not included in subsequent requests
- **Root cause**: Auth interceptor checking wrong storage key (`auth_token` vs `authToken`)
- **Fixed**: Updated interceptor in `src/api/client.ts:28` to use correct key
```

## Performance Issue

```markdown
## Jan 16, 2026 14:00

- **Problem**: Dashboard takes 8+ seconds to load
- **Profiled**: React DevTools shows 47 re-renders on mount
- **Found**: `useEffect` in `StatCard` missing dependency array - runs on every render
- **Fixed**: Added proper deps to `components/StatCard.tsx:23`
- **Result**: Load time down to 1.2 seconds
```

## Failed Approach (Valuable Context)

```markdown
## Jan 17, 2026 09:45

- **Problem**: Need to parse legacy XML config files
- **Tried**: `xml2js` library - worked but lost attribute order
- **Tried**: `fast-xml-parser` - faster but same ordering issue
- **Learned**: Standard XML parsers don't preserve attribute order (not guaranteed by spec)
- **Next**: Try `saxes` for streaming parse with manual order tracking
```

## Architectural Decision

```markdown
## Jan 18, 2026 11:00

- **Context**: Choosing state management for new React Native app
- **Requirements**: Offline-first, sync with backend, <50 entities
- **Considered**: Redux (familiar but boilerplate), Zustand (lighter), TanStack Query + local
- **Decision**: Zustand + TanStack Query with persistence
- **Rationale**: Zustand for UI state, TanStack for server state with offline cache. Avoids Redux ceremony while keeping clear separation.
```

## Multi-Session Investigation

```markdown
## Jan 19, 2026 16:30

- **Continuing**: Intermittent CI failures from Jan 18
- **New info**: Only fails on Ubuntu runners, passes on macOS
- **Tried**: Docker locally with Ubuntu image - reproduced!
- **Found**: Test relies on filesystem case sensitivity (macOS insensitive, Linux sensitive)
- **Fixed**: Corrected import case in `tests/helpers.ts:5` (`Utils` → `utils`)
```

## Quick Fix

```markdown
## Jan 20, 2026 13:15

- **Issue**: Typo in error message confusing users
- **Fixed**: `src/errors/messages.ts:42` - "authenication" → "authentication"
```

## Research/Spike

```markdown
## Jan 21, 2026 10:00

- **Goal**: Evaluate WebSocket libraries for real-time features
- **Reviewed**: socket.io, ws, uWebSockets.js
- **Findings**:
  - socket.io: Full-featured but 95KB bundle, auto-reconnect built-in
  - ws: Minimal (3KB), need to build reconnect logic
  - uWebSockets.js: Fastest but C++ bindings, complex build
- **Recommendation**: socket.io for MVP (dev speed), migrate to ws if bundle size becomes issue
```

## Environment/Config Issue

```markdown
## Jan 22, 2026 08:45

- **Problem**: App crashes on startup in production, works in dev
- **Checked**: Logs show "STRIPE_KEY undefined"
- **Found**: Vercel env vars set but not exposed to client (missing NEXT_PUBLIC_ prefix)
- **Fixed**: Renamed `STRIPE_KEY` → `NEXT_PUBLIC_STRIPE_KEY` in Vercel dashboard
- **Note**: Need to audit other env vars for same issue
```
