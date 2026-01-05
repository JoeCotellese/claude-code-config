---
name: react-native-architect
description: This skill should be used when consulting on React Native feature architecture and design decisions. Use this skill before starting a new feature, when facing design decisions mid-implementation, or when planning refactors. The skill provides component hierarchies, state management strategies, navigation flows, and data flow recommendations with ASCII diagrams, decision matrices, and code scaffolding.
---

# React Native Architect

## Overview

Consult on React Native feature architecture and design. This skill helps plan component hierarchies, decide state management approaches, design navigation flows, structure API integrations, and organize code. It considers existing Wavely patterns as baseline and suggests alternatives when beneficial.

## When to Use

- **Before a new feature**: Design the architecture upfront
- **Mid-implementation decisions**: Choose between approaches (state, navigation, etc.)
- **Refactoring**: Plan migrations or restructures
- **Design review**: Validate proposed architecture

## Consultation Process

### Step 1: Understand the Feature

Gather information by asking:

1. **What is the feature?** High-level goal and user value
2. **What screens/views are needed?** List the UI surfaces
3. **What data is involved?** Entities, relationships, sources (API, local)
4. **Who uses it?** Which user roles (Consumer, Clinical, Caregiver, Commercial)?
5. **What flows exist?** User journeys from start to finish

### Step 2: Load Relevant References

Based on the consultation topic, load from `references/`:

| Topic | Reference |
|-------|-----------|
| Component structure | `references/architecture-patterns.md` |
| State management | `references/state-decisions.md` |
| Navigation design | `references/navigation-patterns.md` |
| API integration | `references/api-patterns.md` |
| Data flow | `references/data-flow.md` |
| Existing patterns | `references/wavely-patterns.md` |

### Step 3: Provide Architecture Outputs

Deliver one or more of:

#### Component Hierarchy Diagram

```
FeatureScreen
├── FeatureContainer (data fetching, state)
│   ├── HeaderSection
│   │   ├── Title
│   │   └── ActionButtons
│   ├── ContentSection
│   │   ├── DataList (FlatList)
│   │   │   └── DataItem (memo)
│   │   └── EmptyState
│   └── FooterSection
│       └── SubmitButton
```

#### File Structure Recommendation

```
src/
├── features/
│   └── newFeature/
│       ├── screens/
│       │   ├── FeatureListScreen.tsx
│       │   └── FeatureDetailScreen.tsx
│       ├── components/
│       │   ├── FeatureCard/
│       │   └── FeatureForm/
│       ├── hooks/
│       │   ├── useFeature.ts
│       │   └── useFeatureList.ts
│       ├── state/
│       │   └── featureState.ts
│       └── index.ts
```

#### State Management Decision

```
┌─────────────────────────────────────────┐
│ Where is [X] state used?                │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
 Single         Parent +        Multiple
Component       Children       Unrelated
    │               │               │
    ▼               ▼               ▼
useState         Props           Recoil

Recommendation: [Decision] because [Reason]
```

#### Navigation Flow Diagram

```
Tab: Features
├── FeatureListScreen
│       │
│       │ onPress(id)
│       ▼
├── FeatureDetailScreen
│       │
│       │ onEdit()
│       ▼
└── FeatureEditScreen (modal)
        │
        │ onSave()
        ▼
    [Navigate back, update cache]
```

#### Decision Matrix

| Approach | Pros | Cons | Fits Wavely? |
|----------|------|------|--------------|
| Option A | Fast, simple | Limited flexibility | Yes, matches BaseApi |
| Option B | Flexible, cacheable | More complexity | Deviation from current |

**Recommendation**: Option [X] because [reasons]

#### Code Scaffolding

```typescript
// hooks/useFeature.ts
function useFeature(featureId: string) {
  const [feature, setFeature] = useRecoilState(featureState(featureId));
  const [loading, setLoading] = useState(!feature);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Fetch logic
  }, [featureId]);

  const updateFeature = useCallback(async (updates) => {
    // Update logic
  }, [featureId]);

  return { feature, loading, error, updateFeature };
}
```

### Step 4: Consider Trade-offs

For each recommendation, address:

1. **Consistency**: Does this follow existing Wavely patterns?
2. **Deviation**: If not, why is the deviation worth it?
3. **Complexity**: Is this the simplest solution that works?
4. **Scalability**: Will this hold up as the feature grows?
5. **Testability**: Can this be easily unit/integration tested?

## Quick Consultations

### "Where should this state live?"

Load `references/state-decisions.md` and apply the decision tree:
- Single component → useState
- Parent + children (2-3 levels) → Props
- Multiple unrelated components → Recoil
- Server data with caching needs → Recoil + async selector or React Query

### "How should I structure this navigation?"

Load `references/navigation-patterns.md` and consider:
- Linear flow → Stack
- Top-level sections → Tabs
- Overlay forms → Modal (presentation: 'modal')
- Quick actions → Bottom sheet (transparentModal)

### "Should I use Recoil or local state?"

Quick rules:
- **useState**: UI state (modal open, accordion), form drafts, ephemeral
- **Recoil**: Shared across screens, persisted, server data cache
- **Props**: Parent-child (1-2 levels), callbacks

### "How do I organize this feature's code?"

Check `references/wavely-patterns.md` for current structure, then:
- Small feature → Add to existing `src/` directories
- Large feature → Consider `src/features/[name]/` with internal structure
- Shared code → `src/shared/` or existing `src/components/`, `src/hooks/`

## Wavely-Specific Guidance

### Existing Patterns (Baseline)

Load `references/wavely-patterns.md` for details on:
- BaseApi extension pattern
- Recoil atom naming (`*State.ts`)
- Hook organization (`src/hooks/`)
- Component structure (directory per component)
- Role-based navigation

### When to Suggest Deviation

Recommend deviation from existing patterns when:

1. **Performance**: Current pattern causes measurable issues
   - Example: Array atom → atomFamily for large lists
2. **Complexity**: Current pattern requires excessive boilerplate
   - Example: BaseApi → React Query for complex caching
3. **Scalability**: Current pattern won't scale for the feature
   - Example: Flat structure → Feature-based for large features
4. **Best practice**: Industry standard has clear benefits
   - Example: Add TypeScript strict mode

Always explain:
- What the current pattern is
- Why deviation is recommended
- What the migration path looks like
- Whether this should apply to existing code or just new code

## Output Templates

### Feature Architecture Document

```markdown
# [Feature Name] Architecture

## Overview
[1-2 sentences describing the feature]

## User Flows
1. [Flow 1 description]
2. [Flow 2 description]

## Component Hierarchy
[ASCII diagram]

## State Management
| State | Location | Reason |
|-------|----------|--------|
| [X] | useState | UI-only, single component |
| [Y] | Recoil | Shared across screens |

## Navigation
[Flow diagram]

## File Structure
[Directory tree]

## API Integration
| Endpoint | Hook | Caching |
|----------|------|---------|
| GET /feature/:id | useFeature | Recoil atom |

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]
```

### Decision Record

```markdown
# Decision: [Topic]

## Context
[What situation prompted this decision]

## Options Considered
1. **Option A**: [Description]
   - Pros: ...
   - Cons: ...
2. **Option B**: [Description]
   - Pros: ...
   - Cons: ...

## Decision
[Which option and why]

## Consequences
- [Impact 1]
- [Impact 2]
```
