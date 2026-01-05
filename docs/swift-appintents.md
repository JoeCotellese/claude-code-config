# Swift App Intents & Shortcuts Reference

Quick reference for implementing App Intents and Shortcuts in iOS/watchOS/visionOS apps.

## Registration & Lifecycle

### 1. Dependency Injection Setup
```swift
// In your App struct's init()
init() {
    // Register dependencies BEFORE intents can run (even in background)
    AppDependencyManager.shared.add(
        dependency: TrailDataManager.shared,
        dependency: NavigationModel.shared,
        dependency: ActivityTracker.shared
    )

    // Register App Shortcuts with system
    TrailShortcuts.updateAppShortcutParameters()
}
```

### 2. Accessing Dependencies in Intents
```swift
struct MyIntent: AppIntent {
    @Dependency
    private var dataManager: DataManager

    @Dependency
    private var navigationModel: NavigationModel
}
```

## Creating App Intents

### Basic Intent Structure
```swift
struct OpenFavorites: AppIntent {
    // Required: Localized title (shown throughout system)
    static let title: LocalizedStringResource = "Open Favorite Trails"

    // Optional: Description for Shortcuts app
    static let description = IntentDescription("Opens your favorite trails.")

    // Control whether app opens when intent runs
    static let openAppWhenRun: Bool = true

    // Use @MainActor if manipulating UI
    @MainActor
    func perform() async throws -> some IntentResult {
        // Do work here
        return .result()
    }
}
```

### Intent with Parameters
```swift
struct GetTrailInfo: AppIntent {
    static let title: LocalizedStringResource = "Get Trail Info"

    @Parameter(title: "Trail", description: "The trail to get information for.")
    var trail: TrailEntity  // Custom AppEntity type

    func perform() async throws -> some IntentResult & ReturnsValue<TrailEntity> {
        return .result(value: trail)
    }
}
```

### Intent with Custom Response (Visual + Voice)
```swift
struct GetTrailInfo: AppIntent {
    @Parameter(title: "Trail")
    var trail: TrailEntity

    func perform() async throws -> some IntentResult & ReturnsValue<TrailEntity> & ProvidesDialog & ShowsSnippetView {
        let snippet = TrailInfoView(trail: trail)
            .background(.clear)  // Use transparent background

        // Full dialog for voice-only contexts, supporting for visual contexts
        let dialog = IntentDialog(
            full: "The latest conditions for \(trail.name) are \(trail.conditions).",
            supporting: "Here's the latest trail information."
        )

        return .result(value: trail, dialog: dialog, view: snippet)
    }
}
```

### Parameter Validation & Disambiguation
```swift
func perform() async throws -> some IntentResult {
    // If parameter is ambiguous, prompt user to choose
    if suggestedMatches.count > 1 {
        let dialog = IntentDialog("Multiple locations match. Did you mean one of these?")
        throw $location.needsDisambiguationError(among: suggestedMatches, dialog: dialog)
    }
}
```

## App Entities (Custom Data Types)

### Define Entity
```swift
struct TrailEntity: AppEntity {
    static let typeDisplayRepresentation = TypeDisplayRepresentation(name: "Trail")

    // Stable, persistent identifier (CRITICAL - used in shortcuts, Spotlight)
    let id: Trail.ID

    // Properties exposed to system via @Property wrapper
    @Property var name: String

    @Property(title: "Region")  // Custom title
    var regionDescription: String

    @Property var difficulty: Difficulty
    @Property var distance: Measurement<UnitLength>

    // Human-readable representation
    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }

    // Register query for this entity
    static let defaultQuery = TrailEntityQuery()
}
```

### Basic Entity Query (Required)
```swift
struct TrailEntityQuery: EntityQuery {
    // REQUIRED: Query by ID
    func entities(for identifiers: [TrailEntity.ID]) async throws -> [TrailEntity] {
        return dataManager.trails(with: identifiers)
            .map { TrailEntity(trail: $0) }
    }

    // OPTIONAL: Suggested entities (shown first in Shortcuts app)
    func suggestedEntities() async throws -> [TrailEntity] {
        return dataManager.favoriteTrails
            .map { TrailEntity(trail: $0) }
    }
}
```

### String Search Query (Optional)
```swift
extension TrailEntityQuery: EntityStringQuery {
    // Enables search field in Shortcuts app
    func entities(matching string: String) async throws -> [TrailEntity] {
        return dataManager.trails { trail in
            trail.name.localizedCaseInsensitiveContains(string)
        }.map { TrailEntity(trail: $0) }
    }
}
```

### Enumerable Query (Small, Fixed Data Sets)
```swift
struct CollectionEntityQuery: EnumerableEntityQuery {
    // Returns ALL entities (use only for small data sets)
    func allEntities() async throws -> [CollectionEntity] {
        return dataManager.allCollections
    }
}
```

### Property Query (Large Data Sets - Enables Find Intent)
```swift
extension TrailEntityQuery: EntityPropertyQuery {
    static var sortingOptions: [EntityQuerySort<TrailEntity>] {
        [
            .init(\.$name, name: "Name", isDefault: true),
            .init(\.$distance, name: "Distance"),
            .init(\.$difficulty, name: "Difficulty")
        ]
    }

    static var properties: [QueryProperty<TrailEntity, TrailEntityQuery>] {
        QueryProperty(\.$name) { name in
            StringComparator.containsString(name)
        }
        QueryProperty(\.$distance) { distance in
            NumericComparator.equalTo(distance)
        }
        // Add more property comparators as needed
    }

    func entities(
        matching comparators: [QueryComparator<TrailEntity>],
        mode: ComparatorMode,
        sortedBy: [EntityQuerySort<TrailEntity>],
        limit: Int?
    ) async throws -> [TrailEntity] {
        // Implement predicate-based search
        // See TrailEntityQuery+PropertyQuery.swift for full implementation
    }
}
```

## App Shortcuts

### Define App Shortcuts Provider
```swift
struct TrailShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenFavorites(),
            phrases: [
                "Open Favorites in \(.applicationName)",
                "Show my favorite \(.applicationName)"
            ],
            shortTitle: "Open Favorites",
            systemImageName: "star.circle"
        )

        AppShortcut(
            intent: StartActivity(),
            phrases: [
                "Start tracking in \(.applicationName)",
                "Begin activity in \(.applicationName)"
            ],
            shortTitle: "Start Activity",
            systemImageName: "figure.walk"
        )
    }
}
```

### Best Practices for App Shortcuts
- **Limit to 2-5 shortcuts** (most common actions, max 10)
- **Always include `\(.applicationName)` in phrases** for proper attribution
- **Localize phrases** in `AppShortcuts.xcstrings`
- **Register during app init**: `TrailShortcuts.updateAppShortcutParameters()`
- **Call update when shortcuts change**: If you modify app shortcuts programmatically

### Siri Tip View
```swift
// Show tip to teach users the phrase
SiriTipView(intent: OpenFavorites(), isVisible: $displaySiriTip)
```

### Info.plist Color Configuration
```xml
<!-- Add to Info.plist for better App Shortcuts presentation -->
<key>NSAppIconActionTintColorName</key>
<string>AccentColor</string>
<key>NSAppIconComplementingColorNames</key>
<array>
    <string>ComplementColor1</string>
    <string>ComplementColor2</string>
</array>
```

## Spotlight Integration

### Make Entity Indexable
```swift
extension TrailEntity: IndexedEntity {
    // Already conforms through AppEntity
}
```

### Associate Entity with Searchable Items
```swift
func indexTrails() async {
    let searchableItems = trails.map { trail in
        let item = CSSearchableItem(
            uniqueIdentifier: String(trail.id),
            domainIdentifier: nil,
            attributeSet: trail.searchableAttributes
        )

        let entity = TrailEntity(trail: trail)
        let priority = trail.isFavorite ? 10 : 1

        // CRITICAL: Associate BEFORE adding to index
        item.associateAppEntity(entity, priority: priority)

        return item
    }

    let index = CSSearchableIndex.default()
    try await index.indexSearchableItems(searchableItems)
}
```

### Searchable Attributes
```swift
var searchableAttributes: CSSearchableItemAttributeSet {
    let attributes = CSSearchableItemAttributeSet()
    attributes.title = name
    attributes.namedLocation = regionDescription
    attributes.keywords = activities.localizedElements
    attributes.latitude = NSNumber(value: coordinate.latitude)
    attributes.longitude = NSNumber(value: coordinate.longitude)
    attributes.supportsNavigation = true
    return attributes
}
```

## Universal Links Integration

### URL Representable Entity
```swift
extension TrailEntity: URLRepresentableEntity {
    static var urlRepresentation: URLRepresentation {
        // Use string interpolation with entity properties
        "https://example.com/trail/\(.id)/details"
    }
}
```

### URL Representable Intent (Skip perform() Implementation)
```swift
struct OpenTrail: AppIntent, OpenIntent, URLRepresentableIntent {
    static let title: LocalizedStringResource = "Open Trail"

    @Parameter(title: "Trail")
    var trail: TrailEntity

    // NO perform() needed - system automatically uses universal link handling
}
```

## Platform-Specific Features

### Apple Watch Action Button
```swift
// Intents conforming to StartWorkoutIntent are automatically available
struct StartActivity: AppIntent, StartWorkoutIntent {
    // Can donate intent to dynamically change Action button behavior
    func perform() async throws -> some IntentResult {
        let result = try await startActivity()

        // Update Action button contextually
        return .result().donate(actionButtonIntent: self)
    }
}
```

## Threading & Lifecycle

- **Intents run on arbitrary queue** - don't assume main thread
- **UI manipulation requires `@MainActor`** on `perform()`
- **Dependencies injected automatically** via `@Dependency`
- **Intents may run while app in background** - ensure dependencies are registered early
- **Return types**: `IntentResult`, `ReturnsValue<T>`, `ProvidesDialog`, `ShowsSnippetView`

## Common Patterns

### When to Use Each Query Type
- **EntityQuery**: Required for all entities (query by ID + suggestions)
- **EntityStringQuery**: Enable search field in Shortcuts app
- **EnumerableEntityQuery**: Small, fixed data sets (returns all entities)
- **EntityPropertyQuery**: Large data sets, enables Find intent with predicates

### Data Consistency Rules
- Entity IDs must be **stable and persistent** (used in shortcuts, Spotlight, URLs)
- `TrailEntity.id` should match internal model ID (`Trail.id`)
- Never change entity IDs after creation

### When Modifying Intents
- Call `AppShortcuts.updateAppShortcutParameters()` if App Shortcuts change
- Update Spotlight index if entity structure changes
- Maintain stable identifiers
- Consider both voice-only and visual contexts for responses

## Debugging

### Logging
```swift
import OSLog

extension Logger {
    static let intentLogging = Logger(subsystem: "com.example.app", category: "Intents")
    static let entityQueryLogging = Logger(subsystem: "com.example.app", category: "EntityQuery")
}

// In intent code
Logger.intentLogging.debug("Intent started with parameter: \(someValue)")
```

### Testing Checklist
1. Build and run on simulator/device
2. Test in Shortcuts app
3. Test with Siri using App Shortcuts phrases
4. Search Spotlight for entity data
5. Check Xcode Console for intent execution logs
6. Verify intents work when app is in background
