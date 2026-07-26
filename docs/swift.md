# Swift & SwiftUI Coding Standards

Decisions, not tutorial. Anything not decided here follows current Swift and
SwiftUI practice. For framework specifics use `mcp__xcode__DocumentationSearch`.

## Platform

- Minimum iOS 18.0
- Swift 6, strict concurrency checking on
- SwiftUI only. UIKit needs a reason
- SwiftData for persistence, configured to disk in production, not in-memory
- Swift Testing (`@Test`), not XCTest
- async/await throughout. Never completion handlers

## State

`@Observable` on every state-holding class, with explicit actor isolation.

Never use `@StateObject`, `@ObservedObject`, `@Published`, or
`@EnvironmentObject`. `@State` creates and owns, `@Environment` receives.

Model complex view state as one enum rather than parallel booleans, so invalid
combinations cannot be represented:

```swift
enum ViewState {
    case idle, loading, loaded(Data), error(Error)
}
```

Same for sheets: one `Identifiable` enum, one `.sheet(item:)`, cases for each
destination. Prefer computed properties over state that can drift.

## Dependency injection

Protocol-based services, injected through the environment.

- Services are defined by a protocol, named with `-ing` or `-able`
  (`HealthKitManaging`, `Cacheable`)
- Concrete implementations are `@Observable` and take their dependencies via init
- The app creates concrete services and passes them with `.environment()`
- ViewModels take protocol types via init. Views create ViewModels
- Tests and previews inject mocks through the same init

## Navigation

`NavigationStack` driven by a coordinator holding a typed route array, not
`NavigationPath` and not scattered `navigationDestination` calls:

```swift
@Observable @MainActor
final class NavigationCoordinator {
    var path: [Route] = []
    enum Route: Hashable { case book(id: String), player, settings }
}
```

The coordinator goes in the environment. Views call methods on it rather than
mutating `path` directly.

## Models

Structs, immutable by default, explicit `Sendable`. Conformance in this order:

```swift
struct User: Codable, Sendable, Identifiable, Hashable { }
```

`Identifiable` for list items, `Hashable` for navigation destinations.

## Testing

Test production behavior through public APIs: user-facing behavior, edge cases,
error paths, integration points.

Do not test mocks, stubs, private methods, trivial accessors, or no-op
implementations. A test that exercises test infrastructure is not a test.

Organization:
- Test file name matches the type under test. `AudioPlayerTests.swift` tests
  `AudioPlayer`
- A test belongs to whichever type it primarily exercises. Timer behavior goes
  in the timer tests even if audio is involved
- Multi-component scenarios get their own `*FlowTests.swift`
- Match actor isolation: a `@MainActor` type gets a `@MainActor` test struct

Delete on sight:
- Assertions against a mock's own call flags
- `#expect(true)` and other meaningless assertions
- `Task.sleep()` timing hacks. Refactor the production code instead
- Duplicate coverage across files

## Views

- Under 200 lines. Extract components past that
- A preview for every view, including states worth seeing (loading, error)
- Modifiers ordered specific to general. Repeated chains become view extensions

## Anti-patterns

Never poll. Use `.onChange` against observable state, `await` a one-shot
operation, or bridge a callback API with a continuation.

## Logging

`AppLogger` with a subsystem: `.ui`, `.network`, `.database`, `.sync`, `.auth`,
`.general`. Injectable as `Logging` so tests can pass `MockLogger`.

Every message is prefixed with a `[FeatureName]` tag for filtering:

```swift
logger.debug("[PhotoPicker] Processing data")
logger.info("[Wine] Saved with ID: \(id)")
logger.warning("[Sync] Asset not found")
logger.logError("[CoreData] Save failed", error: e)
logger.logFault("[Firebase] Corruption", error: e)
```

Never log passwords, tokens, or PII.

## Dependencies

Native first: URLSession, AsyncImage, the Security framework, OSLog. Reach for
a package only when it earns the dependency, and check Swift 6 support first.
Ones that have earned it before:

- Images: Kingfisher or Nuke, when caching and processing get real
- Keychain: KeychainAccess, for the API alone
- Crash reporting: Sentry
- Analytics: TelemetryDeck, for the privacy posture
- Quality: SwiftLint and SwiftFormat

Swift Package Manager only.

## Versioning

`YYYY.MM.Build`, for example `2025.10.1`. Increment the build for each release
and tag it in git.
