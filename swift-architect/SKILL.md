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

### 1. Architectural Analysis

When presented with a feature or problem:

1. **Clarify requirements** - Ask targeted questions to understand scope
2. **Identify components** - Break down into Views, ViewModels, Models, Services
3. **Map data flow** - How data moves through the system
4. **Recommend patterns** - MVVM, Repository, Coordinator, etc.
5. **Provide scaffolding** - Starter code structure

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

### Step 1: Understand the Problem

Ask clarifying questions:
- What is the feature trying to accomplish?
- What data does it need? Where does it come from?
- How does user interaction flow?
- What existing code/patterns are in the codebase?

### Step 2: Analyze and Recommend

1. **Break down components** - Identify all Views, Models, Services needed
2. **Map relationships** - Draw component diagram showing dependencies
3. **Choose patterns** - Recommend architecture with rationale
4. **Identify risks** - Note complexity, edge cases, potential issues

### Step 3: Provide Implementation Guidance

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

**Clarifying Questions**:
1. Should edits save immediately or require explicit save?
2. Can users cancel and discard changes?
3. Is there validation (required fields, character limits)?

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
