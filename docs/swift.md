# Swift & SwiftUI Coding Standards

## Platform Requirements

- **Minimum iOS**: iOS 18.0
- **Language**: Swift 6 with strict concurrency checking enabled
- **UI Framework**: SwiftUI only (no UIKit unless absolutely necessary)
- **State Management**: `@Observable` macro (Observation framework)
- **Data Persistence**: SwiftData
- **Navigation**: NavigationStack with path-based routing
- **Testing**: Swift Testing framework (`@Test` macro)
- **Concurrency**: async/await with full Sendable compliance

## Core Principles

1. **State-Driven UI**: UI is a pure function of state. No imperative updates.
2. **Protocol-Based DI**: All services defined by protocols for testing
3. **Environment Injection**: Pass `@Observable` objects via `.environment()`
4. **Explicit Concurrency**: All types have clear actor isolation
5. **Test Everything**: Services and ViewModels require unit tests

## Dependency Injection Pattern

Use **protocol-based services with environment injection** for testability and maintainability.

### Core Principles
1. **Protocol-First Design**: All services defined by protocols
2. **@Observable Implementation**: Concrete services use `@Observable` macro
3. **Environment Injection**: Pass services via `.environment()`
4. **Constructor Injection**: Services receive their dependencies via init
5. **Mock Support**: Protocol conformance enables test mocks

### Service Layer Pattern

```swift
// 1. Define protocol
protocol APIManaging {
    func fetchUser(id: String) async throws -> User
}

// 2. @Observable concrete implementation
@Observable
@MainActor
final class APIManager: APIManaging {
    private let session: URLSession
    var lastError: Error?

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetchUser(id: String) async throws -> User {
        // Implementation
    }
}

// 3. Mock for testing
final class MockAPIManager: APIManaging {
    var fetchUserResult: Result<User, Error> = .failure(TestError.notSet)

    func fetchUser(id: String) async throws -> User {
        try fetchUserResult.get()
    }
}
```

### ViewModel/Service Pattern

```swift
@Observable
@MainActor
final class ProfileViewModel {
    private let apiManager: APIManaging

    var user: User?
    var isLoading = false
    var errorMessage: String?

    // Dependency injected via init
    init(apiManager: APIManaging) {
        self.apiManager = apiManager
    }

    func loadProfile(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            user = try await apiManager.fetchUser(id: id)
        } catch {
            errorMessage = "Failed to load profile"
        }
    }
}
```

### View Integration

```swift
// App/Root level: Create concrete services
@main
struct MyApp: App {
    @State private var apiManager = APIManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(apiManager)  // Pass via environment
        }
    }
}

// Views: Receive via @Environment
struct ContentView: View {
    @Environment(APIManager.self) private var apiManager
    @State private var viewModel: ProfileViewModel

    init() {
        // Create ViewModel - will inject from environment in body
        _viewModel = State(initialValue: ProfileViewModel(apiManager: APIManager()))
    }

    var body: some View {
        // For views that need the ViewModel
        ProfileView(viewModel: viewModel)
    }
}

// Alternative: Create ViewModel in view when environment available
struct ProfileView: View {
    @Environment(APIManager.self) private var apiManager
    @State private var viewModel: ProfileViewModel?

    var body: some View {
        Group {
            if let viewModel {
                ProfileContent(viewModel: viewModel)
            }
        }
        .onAppear {
            if viewModel == nil {
                viewModel = ProfileViewModel(apiManager: apiManager)
            }
        }
    }
}
```

### Testing Pattern

```swift
import Testing
@testable import MyApp

@MainActor
struct ProfileViewModelTests {
    @Test func loadProfileSuccess() async throws {
        let mockAPI = MockAPIManager()
        mockAPI.fetchUserResult = .success(User(id: "1", name: "Test"))

        let viewModel = ProfileViewModel(apiManager: mockAPI)

        await viewModel.loadProfile(id: "1")

        #expect(viewModel.user?.name == "Test")
        #expect(viewModel.errorMessage == nil)
    }
}
```

### Preview Pattern

```swift
#Preview {
    @Previewable @State var apiManager = MockAPIManager()
    ContentView()
        .environment(apiManager)
}
```

### Dependency Rules

- **App Level**: Create concrete services, inject via `.environment()`
- **Services**: Receive dependencies via init (constructor injection)
- **ViewModels**: Receive dependencies via init using protocol types
- **Views**: Receive services via `@Environment`, create ViewModels
- **Tests**: Inject mocks via init
- **Previews**: Use mocks or preview-specific implementations

## State Management

### Observation Framework (@Observable)

**All state-holding classes use `@Observable` macro:**

```swift
@Observable
@MainActor
final class AuthService {
    var isAuthenticated = false
    var isLoading = false
    var errorMessage: String?

    // Properties auto-tracked - no @Published needed

    func login(username: String, password: String) async throws {
        isLoading = true
        defer { isLoading = false }
        // Login logic
    }
}
```

### Property Wrapper Guide

**Use `@State` for:**
- Local view state (text fields, toggles, selections)
- Creating `@Observable` object instances
- Primitive types owned by the view

```swift
@State private var username = ""
@State private var authService = AuthService()
@State private var selectedTab = 0
```

**Use `@Environment` for:**
- Receiving `@Observable` objects from ancestor views
- Reading system environment values

```swift
@Environment(AuthService.self) private var authService
@Environment(\.modelContext) private var modelContext
```

**NEVER use:**
- `@StateObject` - replaced by `@State`
- `@ObservedObject` - replaced by `@Environment`
- `@Published` - not needed with `@Observable`
- `@EnvironmentObject` - replaced by typed `@Environment`

### State-Driven UI Pattern

**UI is a pure function of state - no imperative updates:**

```swift
@Observable
@MainActor
final class LoginViewModel {
    var username = ""
    var password = ""
    var isLoading = false
    var errorMessage: String?

    // Computed properties for derived state
    var isLoginButtonEnabled: Bool {
        !username.isEmpty && !password.isEmpty && !isLoading
    }

    var loginButtonTitle: String {
        isLoading ? "Logging in..." : "Login"
    }

    func login() async {
        isLoading = true
        defer { isLoading = false }
        // Logic
    }
}

struct LoginView: View {
    @State private var viewModel = LoginViewModel()

    var body: some View {
        Form {
            TextField("Username", text: $viewModel.username)
            SecureField("Password", text: $viewModel.password)

            if let error = viewModel.errorMessage {
                Text(error).foregroundStyle(.red)
            }

            Button(viewModel.loginButtonTitle) {
                Task { await viewModel.login() }
            }
            .disabled(!viewModel.isLoginButtonEnabled)
        }
    }
}
```

### Rules
- Prefer computed properties over redundant state
- Use `defer` for cleanup in async methods
- Keep view models focused and testable
- Implement proper task cancellation

## Navigation Pattern

### NavigationStack with Path-Based Routing

**Use typed path arrays with enum routes for type-safe navigation:**

```swift
@Observable
@MainActor
final class NavigationCoordinator {
    var path: [Route] = []

    enum Route: Hashable {
        case library(id: String)
        case book(id: String)
        case player
        case settings
    }

    func navigateToBook(_ id: String) {
        path.append(.book(id: id))
    }

    func navigateToPlayer() {
        path.append(.player)
    }

    func popToRoot() {
        path.removeAll()
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }
}
```

### Integration in App

```swift
@main
struct MyApp: App {
    @State private var coordinator = NavigationCoordinator()

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $coordinator.path) {
                LibraryListView()
                    .navigationDestination(for: NavigationCoordinator.Route.self) { route in
                        switch route {
                        case .library(let id):
                            LibraryDetailView(id: id)
                        case .book(let id):
                            BookDetailView(id: id)
                        case .player:
                            PlayerView()
                        case .settings:
                            SettingsView()
                        }
                    }
            }
            .environment(coordinator)
        }
    }
}
```

### View Usage

```swift
struct LibraryListView: View {
    @Environment(NavigationCoordinator.self) private var coordinator

    var body: some View {
        List(libraries) { library in
            Button(library.name) {
                coordinator.navigateToBook(library.id)
            }
        }
        .navigationTitle("Libraries")
    }
}
```

### Benefits

- **Type Safety**: Compiler enforces valid routes
- **Centralized Logic**: All navigation in one place
- **Testable**: Easy to test navigation state changes
- **Programmatic Control**: Navigate from anywhere with coordinator reference
- **Deep State**: Full navigation stack is observable and modifiable

**Note:** For App Intents/Shortcuts integration, see `appintents.md` for how to expose navigation to Siri and system integrations.

### View State Pattern
Use enum-based state machines for complex view states to prevent invalid state combinations:

```swift
// ❌ Avoid: Multiple state variables that can conflict
@State private var isLoading = false
@State private var hasError = false
@State private var data: Data? = nil

// ✅ Prefer: Single enum representing all states
enum ViewState {
    case idle
    case loading
    case loaded(Data)
    case error(Error)
}
@State private var state: ViewState = .idle
```

### Sheet Management Pattern
```swift
enum SheetType: Identifiable {
    case settings
    case profile(userId: String)
    case confirmation(action: () -> Void)
    
    var id: String {
        switch self {
        case .settings: return "settings"
        case .profile(let id): return "profile-\(id)"
        case .confirmation: return "confirmation"
        }
    }
}

// In your view:
@State private var activeSheet: SheetType?

// Single sheet modifier handles all cases
.sheet(item: $activeSheet) { sheetType in
    switch sheetType {
    case .settings: SettingsView()
    case .profile(let id): ProfileView(userId: id)
    case .confirmation(let action): ConfirmationView(action: action)
    }
}
```

This pattern is essential for:
- Sheet/alert presentation management
- Loading states with data
- Multi-step flows and wizards
- Any UI with mutually exclusive states

Benefits:
- **Type Safety**: Impossible to have conflicting states
- **Clarity**: Self-documenting state transitions
- **Testability**: Easy to test all state combinations
- **SwiftUI Integration**: Works perfectly with `.sheet(item:)` and similar modifiers

## Swift 6 Concurrency

### Actor Isolation

**All types must have explicit actor isolation:**

```swift
// Main actor for UI-related types
@Observable
@MainActor
final class AuthService {
    var isAuthenticated = false
}

// Nonisolated for background work
@Observable
@MainActor
final class APIClient {
    nonisolated func fetchData<T: Decodable & Sendable>() async throws -> T {
        // Background work, no main actor
    }
}

// Actor for isolated mutable state
actor DatabaseManager {
    private var cache: [String: Data] = [:]

    func cached(for key: String) -> Data? {
        cache[key]
    }
}
```

### Sendable Conformance

**All types crossing actor boundaries must be Sendable:**

```swift
// Structs are automatically Sendable if all members are
struct User: Codable, Sendable, Identifiable {
    let id: String
    let name: String
}

// Enums with associated values
enum APIError: Error, Sendable {
    case unauthorized
    case httpError(statusCode: Int, message: String?)
    case networkError(underlying: Error)  // Error is Sendable
}

// Classes need @unchecked Sendable if manually synchronized
final class NetworkClient: @unchecked Sendable {
    private let lock = NSLock()
    private var cache: [String: Data] = [:]

    func getCached(key: String) -> Data? {
        lock.lock()
        defer { lock.unlock() }
        return cache[key]
    }
}
```

### Typed Throws (Swift 6)

```swift
enum ValidationError: Error, Sendable {
    case emptyUsername
    case passwordTooShort
}

func validateCredentials(username: String, password: String) throws(ValidationError) {
    guard !username.isEmpty else {
        throw .emptyUsername
    }
    guard password.count >= 8 else {
        throw .passwordTooShort
    }
}

// Caller gets typed error
do {
    try validateCredentials(username: user, password: pass)
} catch let error as ValidationError {
    switch error {
    case .emptyUsername:
        message = "Username required"
    case .passwordTooShort:
        message = "Password must be 8+ characters"
    }
}
```

### Async/Await Rules

- NEVER use completion handlers - always use async/await
- Use `Task { }` in views to call async methods
- Use `defer` for cleanup in async functions
- Implement proper task cancellation with `.task` modifier
- Mark async closures: `var onComplete: (() async -> Void)?`

## Models & Data Types

### Protocol Conformance Order

**Follow this order for consistency:**

```swift
struct User: Codable, Sendable, Identifiable, Hashable {
    let id: String
    let name: String
}
```

Order: `Codable, Sendable, Identifiable, Equatable, Hashable`

### Model Rules

- Prefer `struct` for models (value types)
- Always add `Sendable` conformance explicitly
- Use `Identifiable` for list items
- Use `Hashable` for navigation destinations
- Immutable by default - use `let` unless mutability required

## SwiftData Best Practices

- Models use the `@Model` macro
- All models must be `Sendable` compatible
- Configure to persist to disk (not in-memory) for production
- Access context via `@Environment(\.modelContext)`
- Use `@Query` for fetching data in views
- Define clear relationships between models
- Use transactions for bulk operations

## Feature Implementation Guidelines

### When Adding New Features

1. **Define protocols** for any external dependencies
2. **Create @Observable services** implementing protocols
3. **Build ViewModels** using @Observable with injected dependencies
4. **Create SwiftUI views** receiving services via @Environment
5. **Add SwiftData models** if persistence needed (must be Sendable)
6. **Write tests** using Swift Testing with mock dependencies
7. **Use enum-based state** for complex UI states
8. **Add previews** for all views

### Project Structure

```
AppName/
├── AppNameApp.swift                 # App entry, dependency setup
├── Features/
│   ├── Auth/
│   │   ├── Views/
│   │   │   ├── LoginView.swift
│   │   │   └── SignupView.swift
│   │   ├── ViewModels/
│   │   │   └── AuthViewModel.swift
│   │   └── Services/
│   │       ├── AuthManaging.swift   # Protocol
│   │       └── AuthService.swift    # @Observable implementation
│   ├── Library/
│   │   ├── Views/
│   │   ├── ViewModels/
│   │   └── Models/
│   └── Shared/
│       ├── Services/                # Shared services (API, Database)
│       ├── Components/              # Reusable UI components
│       ├── Models/                  # Shared models
│       └── Navigation/              # NavigationCoordinator
├── AppNameTests/                    # Unit tests
└── AppNameUITests/                  # UI tests
```

### File Documentation

**Recommended:** Add ABOUTME comments to complex files for easy grepping:

```swift
// ABOUTME: Handles user authentication and token management
// ABOUTME: Coordinates with Keychain for secure token storage

import Foundation

@Observable
@MainActor
final class AuthService: AuthManaging {
    // ...
}
```

## Testing Standards

### Testing Philosophy

**Test production code behavior, not test infrastructure.**

#### What to Test ✅
- **Public APIs** - The contract your code exposes to callers
- **User-facing behavior** - Features users interact with
- **Edge cases** - Boundary conditions, empty collections, nil values
- **Error paths** - How your code handles failures
- **Integration points** - How components work together in real scenarios

#### What NOT to Test ❌
- **Mocks, stubs, or test helpers** - These are implementation details of testing
- **Private methods** - Test through the public API instead
- **Trivial code** - Simple getters/setters, data classes
- **No-op implementations** - Silent/preview/stub classes that do nothing
- **Implementation details** - Internal state, private properties

#### Test Organization Rules

1. **File naming matches what's tested**
   - `MeditationTimerModelTests.swift` → tests `MeditationTimerModel`
   - `AudioPlayerTests.swift` → tests `AudioPlayer`

2. **If your test primarily exercises ClassA, put it in ClassATests**
   - Timer behavior tests go in timer tests, not audio tests

3. **Integration tests get their own file**
   - `FeatureFlowTests.swift` for multi-component scenarios

### Pre-Commit Test Checklist

Before committing tests, verify:

- [ ] Tests focus on **production code**, not test infrastructure (mocks/stubs)
- [ ] Test file name **matches the class being tested**
- [ ] No `Task.sleep()` timing hacks (refactor production code if needed)
- [ ] All assertions are **meaningful** (no `#expect(true)`)
- [ ] Tests verify **behavior**, not implementation details
- [ ] No **duplicate coverage** across test files
- [ ] Test names clearly describe **what behavior is verified**

### Red Flags to Delete

If you see these patterns, **delete the test**:

```swift
// ❌ Testing a mock in isolation
@Test func testMockDoesX() {
    let mock = MockFoo()
    mock.doThing()
    #expect(mock.thingCalled == true)  // Testing test infrastructure!
}

// ❌ Trivial "does it crash" test
@Test func testSilentPlayerDoesNothing() {
    let player = SilentPlayer()
    player.play()
    #expect(true)  // Meaningless!
}

// ❌ Test in wrong file
// In AudioPlayerTests.swift:
@Test func testTimerStarts() {  // This tests the timer, not audio!
    let timer = MeditationTimer()
    timer.start()
}
```

### Good Test Examples

```swift
// ✅ Tests public API behavior
@Test("Timer counts down from duration")
func testTimerCountdown() {
    let timer = MeditationTimer(duration: 60)
    timer.start()
    simulateTime(seconds: 10)
    #expect(timer.remaining == 50)
}

// ✅ Tests error handling
@Test("Timer throws when duration is negative")
func testNegativeDuration() {
    #expect(throws: ValidationError.self) {
        MeditationTimer(duration: -5)
    }
}

// ✅ Tests integration through public API
@Test("Completed timer saves to HealthKit")
func testHealthKitIntegration() {
    let healthKit = MockHealthKit()
    let timer = MeditationTimer(duration: 60, healthKit: healthKit)
    timer.start()
    timer.complete()
    #expect(healthKit.savedSessions.count == 1)
}
```

### Swift Testing Framework

**Use Swift Testing for all tests:**

```swift
import Testing
@testable import MyApp

@MainActor  // Match actor isolation of class under test
struct AuthServiceTests {
    @Test func loginSuccessAuthenticatesUser() async throws {
        let mockAPI = MockAPIManager()
        mockAPI.loginResult = .success(User(id: "1", name: "Test"))

        let service = AuthService(apiManager: mockAPI)

        try await service.login(username: "test", password: "pass")

        #expect(service.isAuthenticated)
        #expect(service.errorMessage == nil)
    }

    @Test func loginFailureSetsError() async throws {
        let mockAPI = MockAPIManager()
        mockAPI.loginResult = .failure(APIError.unauthorized)

        let service = AuthService(apiManager: mockAPI)

        await #expect(throws: APIError.unauthorized) {
            try await service.login(username: "bad", password: "wrong")
        }

        #expect(!service.isAuthenticated)
        #expect(service.errorMessage != nil)
    }

    @Test func logoutClearsState() async throws {
        let service = AuthService(apiManager: MockAPIManager())
        service.isAuthenticated = true

        await service.logout()

        #expect(!service.isAuthenticated)
    }
}
```

### Testing Rules

- Use `@Test` macro for all tests
- Use `#expect()` for assertions
- Use `#expect(throws:)` for error testing
- Match actor isolation (`@MainActor` test struct for `@MainActor` classes)
- Mock dependencies via protocols
- Test async code directly with async test methods
- Test behavior, not implementation
- Write tests before implementation (TDD)

## Code Organization

### Import Statements
- Group imports logically (Foundation, SwiftUI, third-party)
- Remove unused imports
- Use `@testable import` only in test files

### Access Control
- Mark properties and methods as `private` by default
- Use `internal` only when needed for testing
- Use `public` only for framework/package APIs
- Prefer `private(set)` for read-only properties

### Naming Conventions
- Use descriptive, self-documenting names
- ViewModels: `FeatureNameViewModel` or `FeatureNameModel`
- Protocols: Use `-ing` or `-able` suffix (e.g., `HealthKitManaging`, `Cacheable`)
- Avoid abbreviations except for well-known terms (URL, ID)

## SwiftUI Best Practices

### View Composition

- Keep views small and focused (under 200 lines)
- Extract complex views into separate components
- Use ViewBuilders for reusable view logic
- Prefer composition over inheritance
- Share components between platforms when possible

### Form Inputs

**Always configure text fields properly:**

```swift
TextField("Username", text: $username)
    .textContentType(.username)           // Enables autofill
    .textInputAutocapitalization(.never)  // No auto-caps
    .autocorrectionDisabled()             // No autocorrect

SecureField("Password", text: $password)
    .textContentType(.password)
```

### Loading States

```swift
Button {
    Task { await viewModel.submit() }
} label: {
    if viewModel.isLoading {
        ProgressView()
    } else {
        Text("Submit")
    }
}
.disabled(viewModel.isLoading)
```

### Previews

**REQUIRED for all views:**

```swift
#Preview {
    @Previewable @State var service = AuthService()
    LoginView()
        .environment(service)
}

#Preview("Loading State") {
    @Previewable @State var service = AuthService()
    service.isLoading = true
    return LoginView()
        .environment(service)
}
```

### Modifiers

- Order modifiers from specific to general
- Extract complex chains into view extensions
- Use custom modifiers for repeated patterns

```swift
extension View {
    func cardStyle() -> some View {
        self
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .shadow(radius: 2)
    }
}
```

### Performance

- Use `@State` for object creation (not `@StateObject`)
- Implement `Equatable` for complex state objects
- Use `.task` modifier for async operations
- Avoid unnecessary re-renders with proper state scoping
- Use `@Environment` to avoid prop drilling

## Platform-Specific Considerations

### iOS/iPadOS
- Follow Apple's Human Interface Guidelines
- Support Dynamic Type for accessibility
- Implement proper keyboard avoidance
- Support both portrait and landscape when appropriate
- Handle safe area appropriately

### watchOS Compatibility
- Design for small screens first
- Minimize text input
- Use Digital Crown for scrolling
- Keep interactions brief
- Share business logic but adapt UI

## Third-Party Libraries

**Prefer native frameworks first, but consider these well-maintained libraries when they add significant value:**

### Networking
- **Native URLSession** - Use for most cases
- Consider: [Alamofire](https://github.com/Alamofire/Alamofire) only for very complex networking needs

### Image Loading
- **Native AsyncImage** - Use for basic cases
- Consider: [Kingfisher](https://github.com/onevcat/Kingfisher) or [Nuke](https://github.com/kean/Nuke) for advanced caching/processing

### Keychain
- **Native Security framework** - Prefer wrapping yourself
- Consider: [KeychainAccess](https://github.com/kishikawakatsumi/KeychainAccess) for simpler API

### Analytics/Crash Reporting
- **OSLog** - Use for logging
- Consider: [Sentry](https://github.com/getsentry/sentry-cocoa) for crash reporting
- Consider: [TelemetryDeck](https://telemetrydeck.com) for privacy-focused analytics

### Development Tools
- **Swift Testing** - Use for tests
- Consider: [SwiftLint](https://github.com/realm/SwiftLint) for code quality enforcement
- Consider: [SwiftFormat](https://github.com/nicklockwood/SwiftFormat) for consistent formatting

### General Rules
- Evaluate if the library justifies the dependency
- Check maintenance status and Swift 6 support
- Prefer Swift Package Manager for dependency management
- Audit security for sensitive operations
- Consider package size impact on app

## Important Notes

### Error Handling
- Always provide user-friendly error messages
- Log technical details but show simple messages to users
- Never expose stack traces or internal errors to users

### Permissions
- Request permissions with clear explanations
- Use purpose strings that explain the value to users
- Handle denied permissions gracefully

### Data Validation
- Validate all user input
- Validate all API responses
- Use typed throws for expected errors

### Versioning
- Use YYYY.MM.Build format (e.g., 2025.10.1)
- Increment build number for each release
- Tag releases in git

### Anti-Patterns to Avoid

**NEVER use polling loops:**

```swift
// ❌ Wrong - polling
while !condition {
    try await Task.sleep(for: .milliseconds(100))
}

// ✅ Correct - reactive
.onChange(of: viewModel.condition) { _, isReady in
    if isReady { handleReady() }
}

// ✅ Correct - async/await
let result = await asyncOperation()
```

**Use the platform's async coordination:**
- async/await for one-shot operations
- onChange/@Observable for state changes
- Continuations to bridge callback APIs

## Logging Pattern

### Setup
```swift
// In ViewModels/Services
private let logger = AppLogger.ui  // or .network, .database, .sync, .auth, .general

// With dependency injection
init(logger: Logging = AppLogger(subsystem: .ui)) {
    self.logger = logger
}
```

### Usage
```swift
// [Context] = feature/component name for log filtering
logger.debug("[PhotoPicker] Processing data")           // Verbose dev info
logger.info("[Wine] Saved with ID: \(id)")             // Important events
logger.warning("[Sync] Asset not found")                // Recoverable issues
logger.logError("[CoreData] Save failed", error: e)     // Handled failures
logger.logFault("[Firebase] Corruption", error: e)      // Critical failures
```

### Rules
- Always prefix with [FeatureName] or [ComponentName] tag
- Never log sensitive data (passwords, tokens, PII)
- Use MockLogger in tests