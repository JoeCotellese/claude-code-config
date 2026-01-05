# Analytics Architecture Patterns

Language-agnostic patterns for maintainable, extensible analytics.

## Core Patterns

### 1. Facade Pattern - Single Entry Point

All analytics calls go through ONE facade. Never call providers directly.

```
┌─────────────────────────────────────────────────────┐
│  Application Code (ViewModels, Components, Hooks)   │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ AnalyticsFacade │  ← Single entry point
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ PostHog │  │Amplitude│  │ Custom  │
    └─────────┘  └─────────┘  └─────────┘
```

**Benefits:**
- Swap/add providers without changing app code
- Consistent event formatting
- Single place for debug logging
- Easy to disable in development

**Implementation Skeleton:**

```
class/object AnalyticsFacade:
    providers: List<AnalyticsProvider>

    function report(event: AnalyticsEvent):
        for provider in providers:
            provider.track(event.name, event.properties)

    function identify(userId: String, traits: Map):
        for provider in providers:
            provider.identify(userId, traits)

    function reset():
        for provider in providers:
            provider.reset()
```

### 2. Strategy Pattern - Swappable Providers

Each analytics provider implements a common interface.

```
interface AnalyticsProvider:
    function track(eventName: String, properties: Map)
    function identify(userId: String, traits: Map)
    function reset()
    function flush()
```

**Provider Implementations:**

```
class PostHogProvider implements AnalyticsProvider:
    function track(eventName, properties):
        PostHog.capture(eventName, properties)

class AmplitudeProvider implements AnalyticsProvider:
    function track(eventName, properties):
        Amplitude.track(eventName, properties)

class DebugProvider implements AnalyticsProvider:
    function track(eventName, properties):
        console.log("[Analytics]", eventName, properties)
```

**Benefits:**
- Add new providers (TelemetryDeck, Mixpanel) without touching existing code
- Easy A/B testing of analytics providers
- Debug provider for development

### 3. Adapter Pattern - Event Mapping

Normalize internal events to provider-specific formats.

```
class EventMapper:
    function mapForProvider(event: AnalyticsEvent, provider: ProviderType):
        // Normalize event name
        name = normalizeEventName(event.name, provider)

        // Add provider-specific properties
        properties = event.properties.copy()
        properties.addAll(getDefaultProperties())

        // Provider-specific transformations
        if provider == PostHog:
            properties["$set"] = getUserTraits()

        return MappedEvent(name, properties)
```

**Common Mappings:**
- Event name casing (snake_case, camelCase, kebab-case)
- Property name prefixes ($set, user_, etc.)
- Reserved property handling
- Timestamp formatting

### 4. Observer Pattern - Event Bus

Allow components to react to analytics events without coupling.

```
class AnalyticsFacade:
    eventSubject: Subject<AnalyticsEvent>

    function report(event):
        eventSubject.emit(event)  // Notify observers
        // ... send to providers

    function observeEvents(): Observable<AnalyticsEvent>:
        return eventSubject.asObservable()
```

**Use Cases:**
- Debug overlay showing recent events
- Trigger side effects on specific events
- Analytics event logging/auditing
- Testing/verification

## Type-Safe Events

Define events as an enum/sealed class with typed properties:

```
enum AnalyticsEvent:
    case screenViewed(screenName: String)
    case buttonTapped(buttonId: String, screenName: String)
    case purchaseCompleted(productId: String, amount: Decimal, currency: String)
    case errorOccurred(errorType: String, message: String, stackTrace: String?)

    property name: String:
        // Returns snake_case event name

    property properties: Map<String, Any>:
        // Returns typed properties as map
```

**Benefits:**
- Compile-time checking of event properties
- Autocomplete for event creation
- Single source of truth for event schema
- Prevents typos in event names

## File Organization

```
analytics/
├── AnalyticsFacade.{ext}        # Main entry point
├── AnalyticsEvent.{ext}         # Event definitions enum
├── AnalyticsProvider.{ext}      # Provider interface
├── EventMapper.{ext}            # Event adaptation logic
└── providers/
    ├── PostHogProvider.{ext}
    ├── AmplitudeProvider.{ext}
    └── DebugProvider.{ext}
```

## Adding a New Event (PM-Friendly)

1. **Find the event enum** (`AnalyticsEvent.{ext}`)
2. **Add new case** following existing patterns:
   ```
   case featureUsed(featureName: String, duration: Int)
   ```
3. **Add name mapping** in the name property
4. **Add properties mapping** in the properties property
5. **Use in code:**
   ```
   analytics.report(.featureUsed(featureName: "timer", duration: 120))
   ```

No provider code changes needed - the facade handles distribution.

## Adding a New Provider

1. Create new file in `providers/`
2. Implement `AnalyticsProvider` interface
3. Register in `AnalyticsFacade` initialization
4. Add any provider-specific mappings to `EventMapper`

## Testing Analytics

```
class MockAnalyticsProvider implements AnalyticsProvider:
    capturedEvents: List<(String, Map)> = []

    function track(name, properties):
        capturedEvents.append((name, properties))

    function assertEventTracked(name: String, properties: Map?):
        // Verify event was captured with expected properties
```

Inject `MockAnalyticsProvider` in tests to verify events without network calls.
