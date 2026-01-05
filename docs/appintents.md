# App Intents Implementation Guide for LLMs

This guide provides patterns and best practices for implementing App Intents in Swift, based on Apple's sample code patterns. Use this as a reference when implementing Shortcuts, Siri integration, and system-wide app actions.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Intent Types](#intent-types)
3. [Entities](#entities)
4. [Entity Queries](#entity-queries)
5. [Parameters](#parameters)
6. [Results & Responses](#results--responses)
7. [App Shortcuts](#app-shortcuts)
8. [Dependency Injection](#dependency-injection)
9. [Error Handling](#error-handling)
10. [Advanced Patterns](#advanced-patterns)

---

## Core Concepts

### Basic Intent Structure

Every intent must have:
- `static let title: LocalizedStringResource` - The intent's display name
- `static let description: IntentDescription` - Optional description for Shortcuts app
- `func perform() async throws -> some IntentResult` - The intent's execution logic

```swift
struct MyIntent: AppIntent {
    static let title: LocalizedStringResource = "My Action"
    static let description = IntentDescription("Does something useful.")

    func perform() async throws -> some IntentResult {
        // Your logic here
        return .result()
    }
}
```

### Key Properties

```swift
// Control foreground behavior
static let openAppWhenRun: Bool = true  // Bring app to foreground

// Control discoverability
static let isDiscoverable = false  // Hide from Shortcuts app

// Customize parameter display
static var parameterSummary: some ParameterSummary {
    Summary("Do something with \(\.$parameter)")
}
```

---

## Intent Types

### 1. Basic AppIntent

For simple actions that don't require special behaviors.

```swift
struct OpenFavorites: AppIntent {
    static let title: LocalizedStringResource = "Open Favorite Trails"
    static let description = IntentDescription("Opens the app and goes to your favorite trails.")
    static let openAppWhenRun: Bool = true

    @Dependency
    private var navigationModel: NavigationModel

    @MainActor
    func perform() async throws -> some IntentResult {
        navigationModel.selectedCollection = favoriteCollection
        return .result()
    }
}
```

**Use when**: Simple app actions that may or may not need UI.

### 2. OpenIntent with URLRepresentableIntent

For intents that open specific content via Universal Links.

```swift
struct OpenTrail: OpenIntent, URLRepresentableIntent {
    static let title: LocalizedStringResource = "Open Trail"
    static let description = IntentDescription("Displays trail details in the app.")

    static var parameterSummary: some ParameterSummary {
        Summary("Open \(\.$target)")
    }

    @Parameter(title: "Trail")
    var target: TrailEntity

    // No perform() method needed - system automatically uses URL from URLRepresentableEntity
}
```

**Use when**: Opening specific entities that have Universal Links.

**Entity must conform to**:
```swift
extension TrailEntity: URLRepresentableEntity {
    static var urlRepresentation: URLRepresentation {
        "https://example.com/trail/\(.id)/details"
    }
}
```

### 3. StartWorkoutIntent

For workout/activity tracking with Apple Watch Action button support.

```swift
struct StartTrailActivity: StartWorkoutIntent {
    static let title: LocalizedStringResource = "Start Trail Activity"
    static let openAppWhenRun: Bool = true

    static let suggestedWorkouts: [StartTrailActivity] = [
        StartTrailActivity(style: .hiking),
        StartTrailActivity(style: .biking)
    ]

    @Parameter(title: "Activity")
    var workoutStyle: ActivityStyle

    var displayRepresentation: DisplayRepresentation {
        ActivityStyle.caseDisplayRepresentations[workoutStyle] ?? "Unknown Activity Style"
    }

    func perform() async throws -> some IntentResult {
        // Start workout logic
        return .result()
    }
}
```

**Use when**: Tracking physical activities, especially with HealthKit integration.

### 4. ForegroundContinuableIntent

For intents that may need to continue in the foreground (e.g., requiring login).

```swift
struct SuggestTrails: ForegroundContinuableIntent {
    static let title: LocalizedStringResource = "Suggest Trails"
    static let openAppWhenRun: Bool = false  // Start in background

    @Dependency
    private var accountManager: AccountManager

    @Dependency
    private var navigationModel: NavigationModel

    func perform() async throws -> some IntentResult & ReturnsValue<[TrailEntity]> {
        // Check if user is logged in
        if !accountManager.loggedIn {
            let dialog = IntentDialog("You aren't logged in. Tap Continue to open the app.")

            throw needsToContinueInForegroundError(dialog) {
                // Configure UI for login
                navigationModel.selectedCollection = nil
                navigationModel.selectedTrail = nil
            }
        }

        // Continue with intent logic
        return .result(value: results)
    }
}
```

**Use when**: Background intent that may need foreground access for authentication or authorization.

---

## Entities

### 1. AppEntity (Queryable Data)

For data that can be queried, like user content or app data.

```swift
struct TrailEntity: AppEntity {
    // Required
    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(
            name: LocalizedStringResource("Trail", table: "AppIntents"),
            numericFormat: LocalizedStringResource("\(placeholder: .int) trails", table: "AppIntents")
        )
    }

    static let defaultQuery = TrailEntityQuery()

    var id: Trail.ID  // Must be unique and persistent

    // Entity properties exposed to intents
    @Property var name: String
    @Property(title: "Region") var regionDescription: String
    @Property var trailLength: Measurement<UnitLength>

    // Non-@Property fields are private to the entity
    var imageName: String
    var currentConditions: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: "\(regionDescription)",
            image: DisplayRepresentation.Image(named: imageName)
        )
    }

    init(trail: Trail) {
        self.id = trail.id
        self.name = trail.name
        self.regionDescription = trail.regionDescription
        self.trailLength = trail.trailLength
        self.imageName = trail.featuredImage
        self.currentConditions = trail.currentConditions
    }
}
```

**Key Points**:
- Use `@Property` for fields that should be queryable or displayed in Shortcuts
- Keep entity lightweight - don't include expensive-to-compute properties
- Create separate entity struct if your model has data that intents don't need

### 2. TransientAppEntity (Non-Queryable Data)

For data that changes constantly or is generated on-demand.

```swift
struct ActivityStatisticsSummary: TransientAppEntity {
    static let typeDisplayRepresentation = TypeDisplayRepresentation(name: "Workout Summary")

    @Property var summaryStartDate: Date
    @Property var workoutsCompleted: Int
    @Property var caloriesBurned: Measurement<UnitEnergy>
    @Property var distanceTraveled: Measurement<UnitLength>

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "Workout Summary",
            subtitle: "You burned \(caloriesBurned.formatted(.measurement(width: .abbreviated, usage: .food))) calories.",
            image: DisplayRepresentation.Image(systemName: "party.popper")
        )
    }
}
```

**Use when**: Returning computed or aggregated data from intents that other shortcuts can use as inputs.

### 3. AppEnum (Fixed Set of Options)

For enumeration types used as intent parameters.

```swift
enum ActivityStyle: String, Codable, Sendable {
    case biking
    case hiking
    case jogging
}

extension ActivityStyle: AppEnum {
    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(
            name: LocalizedStringResource("Activity", table: "AppIntents"),
            numericFormat: LocalizedStringResource("\(placeholder: .int) activities", table: "AppIntents")
        )
    }

    static let caseDisplayRepresentations: [ActivityStyle: DisplayRepresentation] = [
        .biking: DisplayRepresentation(
            title: "Biking",
            subtitle: "Mountain bike ride",
            image: .init(systemName: "figure.outdoor.cycle")
        ),
        .hiking: DisplayRepresentation(
            title: "Hiking",
            subtitle: "A lengthy outdoor walk",
            image: .init(systemName: "figure.hiking")
        ),
        .jogging: DisplayRepresentation(
            title: "Jogging",
            subtitle: "A gentle run",
            image: .init(systemName: "figure.run")
        )
    ]
}
```

**Use when**: Parameter has a fixed set of known values at compile time.

### 4. URLRepresentableEntity

Enables opening entities via Universal Links.

```swift
extension TrailEntity: URLRepresentableEntity {
    static var urlRepresentation: URLRepresentation {
        // Use string interpolation with entity properties
        "https://example.com/trail/\(.id)/details"
    }
}
```

**Use when**: Entities can be opened directly in the app via URLs.

---

## Entity Queries

### 1. Basic EntityQuery

Minimum requirement for queryable entities.

```swift
struct TrailEntityQuery: EntityQuery {
    @Dependency
    var trailManager: TrailDataManager

    // Required: Look up entities by ID
    func entities(for identifiers: [TrailEntity.ID]) async throws -> [TrailEntity] {
        return trailManager.trails(with: identifiers)
            .map { TrailEntity(trail: $0) }
    }

    // Optional: Provide suggested entities (e.g., favorites)
    func suggestedEntities() async throws -> [TrailEntity] {
        return trailManager.trails(with: trailManager.favoritesCollection.members)
            .map { TrailEntity(trail: $0) }
    }
}
```

### 2. EntityStringQuery

Adds text search capability.

```swift
extension TrailEntityQuery: EntityStringQuery {
    func entities(matching string: String) async throws -> [TrailEntity] {
        return trailManager.trails { trail in
            trail.name.localizedCaseInsensitiveContains(string)
        }.map { TrailEntity(trail: $0) }
    }
}
```

**Enables**: Searching for entities by name in Shortcuts app.

### 3. EntityPropertyQuery

Adds complex predicate-based searching with a Find intent.

```swift
extension TrailEntityQuery: EntityPropertyQuery {
    typealias ComparatorMappingType = Predicate<TrailEntity>

    static let properties = QueryProperties {
        Property(\TrailEntity.$name) {
            ContainsComparator { searchValue in
                #Predicate<TrailEntity> { $0.name.localizedStandardContains(searchValue) }
            }
            EqualToComparator { searchValue in
                #Predicate<TrailEntity> { $0.name == searchValue }
            }
        }

        Property(\TrailEntity.$trailLength) {
            LessThanOrEqualToComparator { searchValue in
                #Predicate<TrailEntity> { $0.trailLength <= searchValue }
            }
            GreaterThanOrEqualToComparator { searchValue in
                #Predicate<TrailEntity> { $0.trailLength >= searchValue }
            }
        }
    }

    static let sortingOptions = SortingOptions {
        SortableBy(\TrailEntity.$name)
        SortableBy(\TrailEntity.$trailLength)
    }

    static var findIntentDescription: IntentDescription? {
        IntentDescription("Search for trails matching your criteria.",
                          categoryName: "Discover",
                          resultValueName: "Trails")
    }

    func entities(matching comparators: [Predicate<TrailEntity>],
                  mode: ComparatorMode,
                  sortedBy: [EntityQuerySort<TrailEntity>],
                  limit: Int?) async throws -> [TrailEntity] {
        var matchedTrails = try trails(matching: comparators, mode: mode)

        // Apply sorting
        for sortOperation in sortedBy {
            switch sortOperation.by {
            case \.$name:
                matchedTrails.sort(using: KeyPathComparator(\TrailEntity.name, order: sortOperation.order.sortOrder))
            case \.$trailLength:
                matchedTrails.sort(using: KeyPathComparator(\TrailEntity.trailLength, order: sortOperation.order.sortOrder))
            default:
                break
            }
        }

        // Apply limit
        if let limit, matchedTrails.count > limit {
            matchedTrails.removeLast(matchedTrails.count - limit)
        }

        return matchedTrails
    }

    private func trails(matching comparators: [Predicate<TrailEntity>], mode: ComparatorMode) throws -> [TrailEntity] {
        try trailManager.trails.compactMap { trail in
            let entity = TrailEntity(trail: trail)
            var includeAsResult = mode == .and ? true : false
            let earlyBreakCondition = includeAsResult

            for comparator in comparators {
                guard includeAsResult == earlyBreakCondition else { break }
                includeAsResult = try comparator.evaluate(entity)
            }

            return includeAsResult ? entity : nil
        }
    }
}
```

**Creates**: Automatic "Find [Entity]" intent in Shortcuts with complex filtering UI.

### 4. EnumerableEntityQuery

For small, fixed sets of entities where you can return all at once.

```swift
struct FeaturedCollectionEntityQuery: EnumerableEntityQuery {
    static var findIntentDescription: IntentDescription? {
        IntentDescription("Find a featured trail collection.",
                          categoryName: "Discover",
                          resultValueName: "Trails")
    }

    @Dependency
    private var trailManager: TrailDataManager

    func entities(for identifiers: [TrailCollection.ID]) async throws -> [TrailCollection] {
        return trailManager.featuredTrailCollections
            .filter { identifiers.contains($0.id) }
    }

    func suggestedEntities() async throws -> [TrailCollection] {
        return Array(trailManager.featuredTrailCollections.prefix(5))
    }

    // Required for EnumerableEntityQuery
    func allEntities() async throws -> [TrailCollection] {
        return trailManager.featuredTrailCollections
    }
}
```

**Use when**: Entity set is small and can be loaded in memory. Creates simpler Find intent than EntityPropertyQuery.

---

## Parameters

### Basic Parameter Declaration

```swift
@Parameter(title: "Trail", description: "The trail to get information for.")
var trail: TrailEntity
```

### Parameter with Dynamic Options

```swift
@Parameter(
    requestValueDialog: "Where would you like to go?",
    optionsProvider: LocationOptionsProvider()
)
var location: String?
```

**Options Provider**:
```swift
struct LocationOptionsProvider: DynamicOptionsProvider {
    @Dependency
    private var trailManager: TrailDataManager

    func results() async throws -> [String] {
        return trailManager.uniqueLocations
            .sorted(using: KeyPathComparator(\.self, comparator: .localizedStandard))
    }
}
```

### Measurement Parameters

```swift
@Parameter(defaultUnit: .kilometers, supportsNegativeNumbers: false)
var searchRadius: Measurement<UnitLength>?
```

**Usage in intent**:
```swift
if var searchRadius {
    // Convert to app's internal unit
    searchRadius.convert(to: .meters)
    // Use searchRadius.value
}
```

### Parameter Validation

```swift
private func validateParameters() async throws {
    // Check if required parameter has value
    if location == nil && searchRadius == nil {
        throw $location.needsValueError(IntentDialog("Please provide a location."))
    }

    // Validate string parameter value
    if let location {
        let uniqueLocations = trailManager.uniqueLocations

        if !uniqueLocations.contains(location) {
            let suggestedMatches = uniqueLocations.filter { $0.contains(location) }

            if suggestedMatches.count == 1 {
                // Request confirmation for close match
                let suggestion = suggestedMatches.first!
                let dialog = IntentDialog("Did you mean \(suggestion)?")
                let confirmed = try await $location.requestConfirmation(for: suggestion, dialog: dialog)
                if confirmed {
                    self.location = suggestion
                } else {
                    throw $location.needsValueError()
                }
            } else if !suggestedMatches.isEmpty && suggestedMatches.count < 5 {
                // Disambiguate between multiple matches (keep under 5 for voice UX)
                let dialog = IntentDialog("Multiple locations match \(location). Did you mean one of these?")
                throw $location.needsDisambiguationError(among: suggestedMatches, dialog: dialog)
            } else {
                // No matches or too many
                throw $location.needsValueError(IntentDialog("There are no locations that match \(location)."))
            }
        }
    }
}
```

### Parameter Summaries

#### Simple Summary
```swift
static var parameterSummary: some ParameterSummary {
    Summary("Get information for \(\.$trail)")
}
```

#### Conditional Summary
```swift
static var parameterSummary: some ParameterSummary {
    When(\.$location, .hasAnyValue) {
        Summary("Suggest trails near \(\.$location)")
    } otherwise: {
        Summary("Suggest trails from \(\.$trailCollection)")
    }
}
```

#### Complex Switch/Case Summary
```swift
static var parameterSummary: some ParameterSummary {
    Switch(\.$activity) {
        Case(.biking) {
            When(\.$location, .hasAnyValue) {
                Summary("Show \(\.$activity) ideas within \(\.$searchRadius) of \(\.$location)")
            } otherwise: {
                Summary("Show \(\.$activity) ideas from \(\.$trailCollection)")
            }
        }
        DefaultCase() {
            Summary("Suggest \(\.$activity) trails from \(\.$trailCollection) or near \(\.$location)")
        }
    }
}
```

---

## Results & Responses

### Basic Result

```swift
func perform() async throws -> some IntentResult {
    // Do work
    return .result()
}
```

### Result with Value (Composable Shortcuts)

```swift
func perform() async throws -> some IntentResult & ReturnsValue<[TrailEntity]> {
    let results = // ... compute results
    return .result(value: results)
}
```

**Enables**: Other shortcuts can use this intent's output as their input.

### Result with Dialog (Voice Response)

```swift
func perform() async throws -> some IntentResult & ProvidesDialog {
    return .result(dialog: "Your trail day pass is active.")
}
```

**For different contexts**:
```swift
let dialog = IntentDialog(
    full: "The latest conditions for \(trail.name) indicate: \(trail.currentConditions).",
    supporting: "Here's the latest information on trail conditions."
)
return .result(dialog: dialog)
```

- `full`: Used when system can only read (e.g., Siri voice-only)
- `supporting`: Used when system can display UI

### Result with Custom View

```swift
func perform() async throws -> some IntentResult & ShowsSnippetView & ProvidesDialog {
    let snippet = TrailInfoView(trail: trailData, includeConditions: true)
    let dialog = IntentDialog(
        full: "Conditions: \(trail.currentConditions).",
        supporting: "Here's the trail information."
    )
    return .result(view: snippet, dialog: dialog)
}
```

### Combined Result

```swift
func perform() async throws -> some IntentResult & ReturnsValue<TrailEntity> & ProvidesDialog & ShowsSnippetView {
    let snippet = TrailInfoView(trail: trailData, includeConditions: true)
    let dialog = IntentDialog(
        full: "The latest reported conditions for \(trail.name) indicate: \(trail.currentConditions).",
        supporting: "Here's the latest information."
    )
    return .result(value: trail, dialog: dialog, view: snippet)
}
```

---

## App Shortcuts

App Shortcuts make intents discoverable system-wide without requiring users to create them.

### AppShortcutsProvider

```swift
struct TrailShortcuts: AppShortcutsProvider {
    // Optional: Customize tile color in Shortcuts app
    static let shortcutTileColor = ShortcutTileColor.navy

    static var appShortcuts: [AppShortcut] {
        // Simple shortcut
        AppShortcut(intent: OpenFavorites(), phrases: [
            "Open Favorites in \(.applicationName)",
            "Show my favorite \(.applicationName)"
        ],
        shortTitle: "Open Favorites",
        systemImageName: "star.circle")

        // Shortcut with parameter from AppEnum
        // Creates one shortcut per enum case automatically
        AppShortcut(intent: StartTrailActivity(), phrases: [
            "Track my \(\.$workoutStyle) in \(.applicationName)",
            "Start tracking my \(\.$workoutStyle) with \(.applicationName)"
        ],
        shortTitle: "Start Activity",
        systemImageName: "shoeprints.fill")

        // Shortcut with ParameterPresentation
        AppShortcut(intent: GetTrailInfo(), phrases: [
            "Get \(\.$trail) conditions with \(.applicationName)",
            "Get conditions on \(\.$trail) with \(.applicationName)"
        ],
        shortTitle: "Get Conditions",
        systemImageName: "cloud.rainbow.half",
        parameterPresentation: ParameterPresentation(
            for: \.$trail,
            summary: Summary("Get \(\.$trail) conditions"),
            optionsCollections: {
                OptionsCollection(TrailEntityQuery(), title: "Favorite Trails", systemImageName: "cloud.rainbow.half")
            }
        ))
    }
}
```

### Key Rules for App Shortcuts

1. **Phrases must include app name**: Use `\(.applicationName)` placeholder
2. **First shortcut is most important**: Put the most commonly used shortcut first
3. **First shortcut shouldn't open app**: It should work in background for best UX
4. **Localize phrases**: Use `AppShortcuts.xcstrings` string catalog
5. **Update when needed**: Call `TrailShortcuts.updateAppShortcutParameters()` in app init and when parameter values change

### Register in App Init

```swift
@main
struct MyApp: App {
    init() {
        // Set up dependencies...

        // Update app shortcuts
        TrailShortcuts.updateAppShortcutParameters()
    }
}
```

---

## Dependency Injection

App Intents may run in background without your app's UI. Use dependency injection to provide access to app services.

### Register Dependencies

```swift
@main
struct AppIntentsSampleApp: App {
    private var trailManager: TrailDataManager
    private let sceneNavigationModel: NavigationModel

    init() {
        let trailDataManager = TrailDataManager.shared
        trailManager = trailDataManager

        let navigationModel = NavigationModel()
        sceneNavigationModel = navigationModel

        // Register dependencies for App Intents
        AppDependencyManager.shared.add(dependency: trailDataManager)
        AppDependencyManager.shared.add(dependency: navigationModel)

        TrailShortcuts.updateAppShortcutParameters()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(trailManager)
                .environment(sceneNavigationModel)
        }
    }
}
```

### Use Dependencies in Intents

```swift
struct MyIntent: AppIntent {
    @Dependency
    private var trailManager: TrailDataManager

    @Dependency
    private var navigationModel: NavigationModel

    func perform() async throws -> some IntentResult {
        // Dependencies are automatically injected
        let trails = trailManager.allTrails
        navigationModel.selectedTrail = trails.first
        return .result()
    }
}
```

### Use Dependencies in Entity Queries

```swift
struct TrailEntityQuery: EntityQuery {
    @Dependency
    var trailManager: TrailDataManager

    func entities(for identifiers: [TrailEntity.ID]) async throws -> [TrailEntity] {
        return trailManager.trails(with: identifiers)
            .map { TrailEntity(trail: $0) }
    }
}
```

---

## Error Handling

### Custom Localized Errors

```swift
enum TrailIntentError: Error, CustomLocalizedStringResourceConvertible {
    case workoutDidNotStart
    case activeActivityNotFound
    case trailNotFound
    case dayPassTransactionCanceled
    case dayPassPaymentError

    var localizedStringResource: LocalizedStringResource {
        switch self {
        case .workoutDidNotStart:
            return "Workout tracking failed to start."
        case .activeActivityNotFound:
            return "Not currently tracking an activity."
        case .trailNotFound:
            return "Can't find the requested trail."
        case .dayPassTransactionCanceled:
            return "Your purchase was canceled."
        case .dayPassPaymentError:
            return "Unable to process payment."
        }
    }
}
```

### Throw Custom Errors

```swift
func perform() async throws -> some IntentResult {
    guard let trail = trailManager.trail(with: trailID) else {
        throw TrailIntentError.trailNotFound
    }
    // Continue...
}
```

### Parameter Validation Errors

```swift
// Need user to provide a value
throw $location.needsValueError(IntentDialog("Please provide a location."))

// Need user to choose between options
throw $location.needsDisambiguationError(among: options, dialog: IntentDialog("Which location?"))

// Request confirmation for a suggested value
let confirmed = try await $location.requestConfirmation(for: suggestion, dialog: dialog)
```

### Foreground Continuation Error

```swift
if !accountManager.loggedIn {
    let dialog = IntentDialog("You aren't logged in. Tap Continue to open the app.")

    throw needsToContinueInForegroundError(dialog) {
        // Configure UI to help user log in
        navigationModel.selectedCollection = nil
        navigationModel.preferredColumn = .sidebar
    }
}
```

---

## Advanced Patterns

### 1. Confirmation for Destructive Actions

```swift
struct BuyDayPass: AppIntent {
    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        do {
            let passAmount = IntentCurrencyAmount(amount: 6.50, currencyCode: "USD")
            let dialog = IntentDialog("Are you sure you want to purchase for \(passAmount)?")

            // Request confirmation with appropriate action name
            try await requestConfirmation(actionName: .buy, dialog: dialog)

            // Process payment...

        } catch {
            // User canceled
            throw TrailIntentError.dayPassTransactionCanceled
        }

        return .result(dialog: "Your trail day pass is active.")
    }
}
```

**Action names**: `.buy`, `.delete`, `.open`, `.share`, etc.

### 2. Apple Watch Action Button Integration

```swift
struct NextTrailManeuver: AppIntent {
    static let isDiscoverable = false  // Hide from Shortcuts app

    func perform() async throws -> some IntentResult & ProvidesDialog {
        // Do work...

        // Return next intent for Action button to call on next press
        return .result(
            actionButtonIntent: EndTrailActivity(),
            dialog: "Turn right in 300 meters."
        )
    }
}
```

**To configure Action button**:
- Conform intent to `StartWorkoutIntent`
- Set `openAppWhenRun = true`
- Provide `suggestedWorkouts`
- Return `.result(actionButtonIntent:)` OR donate intent with `donate()`

### 3. Transferable Entity for Cross-App Sharing

```swift
extension ActivityStatisticsSummary: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        // Rich text representation
        DataRepresentation(exportedContentType: .rtf) { summary in
            try summary.richTextRepresentation
        }

        // Image representation
        FileRepresentation(exportedContentType: .png) { summary in
            SentTransferredFile(try summary.imageFileRepresentation, allowAccessingOriginalFile: true)
        }
    }
}
```

**Enables**: Sharing entity data with other apps (Notes, Mail, etc.) in various formats.

### 4. Background Authorization Requests

When Action button triggers intent but authorization isn't granted yet:

```swift
func perform() async throws -> some IntentResult {
    if await activityTracker.isActivityTrackingAuthorized {
        try await startActivityTracking()
    } else {
        // Request authorization in Task to avoid blocking Action button overlay
        Task {
            let authorized = try await activityTracker.requestAuthorization()
            if authorized {
                try await startActivityTracking()
            }
        }
    }

    return .result()
}
```

**Pattern**: Immediately return from intent so Action button overlay dismisses, then request authorization asynchronously.

### 5. Complex Parameter Presentation

For App Shortcuts with rich parameter configuration UI:

```swift
AppShortcut(intent: GetTrailInfo(), phrases: [...],
    shortTitle: "Get Conditions",
    systemImageName: "cloud.rainbow.half",
    parameterPresentation: ParameterPresentation(
        for: \.$trail,
        summary: Summary("Get \(\.$trail) conditions"),
        optionsCollections: {
            // Shows EntityQuery results as options
            OptionsCollection(
                TrailEntityQuery(),
                title: "Favorite Trails",
                systemImageName: "cloud.rainbow.half"
            )
        }
    )
)
```

### 6. Logging in Intents

```swift
import OSLog

extension Logger {
    static let intentLogging = Logger(subsystem: "com.example.app", category: "intents")
    static let entityQueryLogging = Logger(subsystem: "com.example.app", category: "entity-query")
}

struct MyIntent: AppIntent {
    func perform() async throws -> some IntentResult {
        Logger.intentLogging.debug("[MyIntent] Starting execution")
        // ...
        Logger.intentLogging.debug("[MyIntent] Completed successfully")
        return .result()
    }
}
```

---

## Implementation Checklist

When implementing App Intents, follow this checklist:

### For Each Intent

- [ ] Define `title` and `description`
- [ ] Set `openAppWhenRun` appropriately
- [ ] Create `parameterSummary` for readability
- [ ] Add parameters with `@Parameter`
- [ ] Validate parameters if needed
- [ ] Inject dependencies with `@Dependency`
- [ ] Use `@MainActor` if touching UI
- [ ] Return appropriate result type (ReturnsValue, ProvidesDialog, ShowsSnippetView)
- [ ] Handle errors with custom localized errors
- [ ] Add logging for debugging

### For Each Entity

- [ ] Define `typeDisplayRepresentation`
- [ ] Define `defaultQuery`
- [ ] Use `@Property` for queryable fields
- [ ] Implement `displayRepresentation`
- [ ] Create entity query
- [ ] Add `URLRepresentableEntity` if applicable
- [ ] Add `Transferable` if sharing with other apps

### For Each Entity Query

- [ ] Implement `entities(for:)` - required
- [ ] Implement `suggestedEntities()` - recommended
- [ ] Add `EntityStringQuery` for text search
- [ ] Add `EntityPropertyQuery` for complex filtering (optional)
- [ ] Define `findIntentDescription` if adding Find intent
- [ ] Inject dependencies with `@Dependency`
- [ ] Add logging

### For App Shortcuts

- [ ] Create `AppShortcutsProvider` struct
- [ ] Define phrases including `\(.applicationName)`
- [ ] Add `shortTitle` and `systemImageName`
- [ ] Put most common shortcut first
- [ ] First shortcut should work in background
- [ ] Add `parameterPresentation` for rich configuration
- [ ] Call `updateAppShortcutParameters()` in app init
- [ ] Create `AppShortcuts.xcstrings` for localization

### For App Setup

- [ ] Register dependencies in `App.init()`
- [ ] Update app shortcuts in `App.init()`
- [ ] Add `@Environment` for UI access to dependencies
- [ ] Test intents run without UI scenes
- [ ] Test with voice-only (Siri)
- [ ] Test in Shortcuts app

---

## Common Patterns Summary

| Pattern | When to Use |
|---------|-------------|
| **Basic AppIntent** | Simple actions, opening app sections |
| **OpenIntent + URLRepresentable** | Opening specific entities via Universal Links |
| **StartWorkoutIntent** | Physical activities, Action button integration |
| **ForegroundContinuableIntent** | Background intents that may need foreground (login, authorization) |
| **AppEntity** | User data that can be queried and saved in shortcuts |
| **TransientAppEntity** | Computed/generated data not stored persistently |
| **AppEnum** | Fixed set of options known at compile time |
| **EntityQuery** | Basic entity lookup by ID |
| **EntityStringQuery** | Add text search to entity |
| **EntityPropertyQuery** | Complex filtering with predicates and Find intent |
| **EnumerableEntityQuery** | Small fixed set of entities with simpler Find intent |
| **DynamicOptionsProvider** | Runtime-determined parameter options |
| **ReturnsValue** | Intent output usable by other shortcuts |
| **ProvidesDialog** | Voice responses for Siri |
| **ShowsSnippetView** | Custom SwiftUI view in results |
| **Transferable** | Sharing entity with other apps in various formats |

---

## File Organization Recommendation

```
MyApp/
├── App Intents/
│   ├── MyAppShortcuts.swift          // AppShortcutsProvider
│   ├── MyIntentError.swift           // Custom errors
│   ├── OpenMyFeature.swift           // Individual intents
│   ├── GetMyData.swift
│   ├── PerformMyAction.swift
│   ├── Entities/
│   │   ├── MyEntity.swift            // AppEntity definitions
│   │   ├── MyEntityQuery.swift       // EntityQuery
│   │   ├── MyEntityQuery+PropertyQuery.swift  // Extensions
│   │   ├── MyOptionsProvider.swift   // DynamicOptionsProvider
│   │   └── MyTransferableEntity+Transferable.swift
│   └── Activity Intents/             // Group related intents
│       ├── StartActivity.swift
│       └── EndActivity.swift
```

---

## Testing Strategies

1. **Test in Shortcuts app**: Create shortcuts using your intents
2. **Test with Siri**: Use voice commands to trigger App Shortcuts
3. **Test background execution**: Ensure intents work without launching app UI
4. **Test parameter validation**: Try invalid inputs, disambiguation flows
5. **Test foreground continuation**: Verify login/authorization flows work
6. **Test Find intent**: Use complex queries with EntityPropertyQuery
7. **Test cross-app sharing**: Use Transferable outputs in other apps
8. **Test Apple Watch**: Test Action button integration if applicable

---

## Additional Resources

- [Apple's App Intents Documentation](https://developer.apple.com/documentation/appintents)
- [WWDC Sessions on App Intents](https://developer.apple.com/videos/play/wwdc2022/10032/)
- Sample: `AcceleratingAppInteractionsWithAppIntents`

---

This guide covers the core patterns found in Apple's sample code. Use these as templates when implementing App Intents, adapting them to your specific app's needs.
