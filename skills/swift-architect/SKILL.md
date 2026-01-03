---
name: swift-architect
description: This skill should be used when consulting on Swift/SwiftUI app architecture and design decisions. Use this before starting a new feature, when facing design decisions mid-implementation, or when planning refactors. Provides component hierarchies, state management strategies, navigation flows, and data flow recommendations with ASCII diagrams, decision matrices, and code scaffolding. Integrates with Apple-Docs MCP for documentation lookups.
---

# Swift Architect

## Overview

Expert architectural consultation for Swift and SwiftUI applications. This skill helps developers think through app architecture before writing code, providing structured analysis, pattern recommendations, and concrete implementation guidance.

## When to Use This Skill

Invoke this skill when:
- Starting a new iOS/macOS feature and need to plan the architecture
- Facing a design decision mid-implementation (state management, navigation, data flow)
- Planning a refactor of existing code
- Unsure which SwiftUI patterns to apply
- Need to understand how Apple frameworks fit together

## Core Capabilities

### 0. Architecture Document Discovery

**Before starting any consultation**, search for existing architecture documentation in the project:

1. **Search locations** (in order of priority):
   - `./ARCHITECTURE.md` or `./Architecture.md`
   - `./docs/ARCHITECTURE.md` or `./docs/architecture.md`
   - `./docs/Architecture.md`
   - `./Documentation/Architecture.md`
   - `./README.md` (may contain architecture section)

2. **Use Glob to find architecture docs:**
   ```
   Glob pattern: "**/[Aa]rchitecture*.md"
   Glob pattern: "**/ARCHITECTURE.md"
   ```

3. **If found**, read and incorporate:
   - Existing patterns and conventions
   - Component naming standards
   - Data flow decisions already made
   - Technology choices and constraints
   - Reference the document in recommendations

4. **If not found**, note this and offer to help create one after the consultation.

### 1. Architectural Analysis

When presented with a feature or problem:

1. **Discover existing architecture** - Search for ARCHITECTURE.md (see above)
2. **Clarify requirements** - Use AskUserQuestion prompt forms (see below)
3. **Identify components** - Break down into Views, ViewModels, Models, Services
4. **Map data flow** - How data moves through the system
5. **Recommend patterns** - MVVM, Repository, Coordinator, etc.
6. **Provide scaffolding** - Starter code structure

### 2. Pattern Recommendations

**State Management**
- `@State` - Local view state, simple values
- `@Binding` - Two-way connection to parent state
- `@StateObject` - View owns the observable object lifecycle
- `@ObservedObject` - View observes but doesn't own
- `@EnvironmentObject` - Dependency injection for deep hierarchies
- `@Environment` - System-provided values

**Architecture Patterns**
- **MVVM** - Standard for SwiftUI, ViewModel as ObservableObject
- **Repository Pattern** - Abstract data sources behind protocols
- **Coordinator Pattern** - Centralized navigation management
- **Service Layer** - Business logic separate from UI

### 3. Documentation Lookup

Use the Apple-Docs MCP server to look up official documentation:

```
# Set technology context for searches
mcp__apple-docs__choose_technology(name: "SwiftUI")

# Search for symbols
mcp__apple-docs__search_symbols(query: "NavigationStack")

# Get detailed documentation
mcp__apple-docs__get_documentation(path: "View")
```

**Always verify recommendations against official Apple documentation** when:
- Recommending specific APIs
- Unsure about availability or deprecation
- Need to understand exact behavior

### 4. Deliverables

When consulting on architecture, provide:

**ASCII Component Diagrams**
```
┌─────────────────────────────────────────────┐
│                   App                        │
├─────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │ ContentView │───▶│ RecipeListViewModel │ │
│  └─────────────┘    └─────────────────────┘ │
│         │                     │             │
│         ▼                     ▼             │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │ RecipeRow   │    │  RecipeRepository   │ │
│  └─────────────┘    └─────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Decision Matrices**
| Approach | Complexity | Testability | Scalability |
|----------|------------|-------------|-------------|
| @State only | Low | Low | Low |
| MVVM | Medium | High | High |
| TCA | High | Very High | Very High |

**Code Scaffolding**
```swift
// MARK: - ViewModel
@MainActor
final class RecipeListViewModel: ObservableObject {
    @Published private(set) var recipes: [Recipe] = []
    @Published private(set) var isLoading = false

    private let repository: RecipeRepositoryProtocol

    init(repository: RecipeRepositoryProtocol) {
        self.repository = repository
    }

    func loadRecipes() async {
        isLoading = true
        defer { isLoading = false }

        do {
            recipes = try await repository.fetchAll()
        } catch {
            // Handle error
        }
    }
}
```

## Consultation Workflow

### Step 1: Discover Existing Architecture

Before asking questions, search for architecture documentation:
```
Glob: "**/[Aa]rchitecture*.md"
Glob: "**/ARCHITECTURE.md"
```

Read any found documents to understand existing patterns, conventions, and constraints.

### Step 2: Gather Requirements via Prompt Forms

**Use the AskUserQuestion tool** to collect clarifying information. Present questions as structured forms rather than free-text lists.

**Initial Context Form:**
```
AskUserQuestion with 2-3 questions:

1. Feature Type (header: "Feature Type")
   - New screen/view
   - New data flow/service
   - Refactor existing code
   - Navigation change
   - State management update

2. Data Source (header: "Data Source")
   - Local only (UserDefaults, SwiftData, files)
   - Remote API
   - Both local and remote
   - No data persistence needed

3. Scope (header: "Scope")
   - Single view component
   - Feature module (multiple views)
   - App-wide change
   - Cross-cutting concern (logging, analytics, etc.)
```

**Follow-up questions** should also use AskUserQuestion when choices are discrete:
- Navigation style → form with options (NavigationStack, sheet, fullScreenCover, custom)
- State ownership → form with options (@State, @StateObject, @EnvironmentObject, etc.)
- Error handling strategy → form with options (local, centralized, Result type, throws)

**When to use free-form questions instead:**
- Asking about specific business requirements
- Understanding edge cases
- Clarifying ambiguous user intent
- Gathering context that doesn't fit predefined options

### Step 3: Analyze and Recommend

1. **Break down components** - Identify all Views, Models, Services needed
2. **Map relationships** - Draw component diagram showing dependencies
3. **Choose patterns** - Recommend architecture with rationale
4. **Identify risks** - Note complexity, edge cases, potential issues

### Step 4: Provide Implementation Guidance

- **File structure** - Where each component lives
- **Protocol definitions** - Contracts between components
- **Starter code** - Scaffolding for key pieces
- **Testing strategy** - How to unit test the architecture

## SwiftUI Best Practices

### View Composition
- Keep views small and focused
- Extract reusable components
- Use ViewBuilder for conditional content
- Prefer composition over inheritance

### Performance
- Use `@State` for local, `@StateObject` for owned observables
- Avoid heavy work in view body
- Use `.task` for async work
- Consider `EquatableView` for expensive views

### Navigation
- iOS 16+: Use `NavigationStack` with `navigationDestination`
- Use type-safe navigation with enums
- Consider Coordinator pattern for complex flows

### Data Flow
- Single source of truth
- Unidirectional data flow where possible
- Use Combine for reactive pipelines
- Prefer async/await over callbacks

## Example Consultation

**User**: "I need to add a recipe editing feature. Users can edit name, ingredients, and steps."

**Architect Response**:

Let me help you design the recipe editing feature.

**Step 1: Check for architecture docs**
```
Glob: "**/[Aa]rchitecture*.md"
→ Found: ./docs/ARCHITECTURE.md
→ Read and note existing patterns (MVVM, Repository pattern in use)
```

**Step 2: Gather requirements via prompt form**
```
AskUserQuestion:

1. Save Behavior (header: "Save")
   - Auto-save on change
   - Explicit save button
   - Save on navigation away

2. Validation (header: "Validation")
   - Required fields only
   - Character limits
   - Custom business rules
   - No validation needed

3. Cancel Behavior (header: "Cancel")
   - Discard with confirmation
   - Discard immediately
   - No cancel option (auto-save)
```

*User selects: Explicit save, Required fields + character limits, Discard with confirmation*

**Proposed Architecture**:

```
┌─────────────────────────────────────────────┐
│              RecipeEditView                  │
│  - Form with TextField, List for ingredients │
│  - Save/Cancel buttons                       │
├─────────────────────────────────────────────┤
│           RecipeEditViewModel                │
│  - @Published draft: Recipe                  │
│  - validate() -> [ValidationError]           │
│  - save() async throws                       │
├─────────────────────────────────────────────┤
│            RecipeRepository                  │
│  - update(_ recipe: Recipe) async throws     │
└─────────────────────────────────────────────┘
```

**Key Decisions**:
- Use a `draft` copy of the Recipe for editing (allows cancel)
- ViewModel handles validation before save
- Repository abstracts persistence

Would you like me to scaffold the ViewModel code?

## GitLab Comment Template

Post architectural decisions as comments on GitLab issues. The issue description stays as the PM perspective; architecture lives in comments.

### Template

```markdown
## Architecture Decision

**Pattern:** [MVVM / Repository / Coordinator / etc.]

**Components:**
| Component | Responsibility |
|-----------|----------------|
| `ComponentName` | What it does |
| `ComponentName` | What it does |

**Data Flow:**
```
[Source] → [Transform] → [Destination]
```

**Key Decisions:**
- Decision 1: Rationale
- Decision 2: Rationale

**File Structure:**
```
Features/FeatureName/
├── Views/
│   └── FeatureView.swift
├── ViewModels/
│   └── FeatureViewModel.swift
└── Models/
    └── Feature.swift
```

**Open Questions:**
- [ ] Question needing async clarification?

**Next Steps:**
1. First implementation step
2. Second implementation step
```

### Usage

1. **Initial architecture comment** - Post when starting work on an issue
2. **Update with answers** - Edit or reply as questions get resolved
3. **Reference in commits** - `Fix #70: ... (see architecture comment)`
