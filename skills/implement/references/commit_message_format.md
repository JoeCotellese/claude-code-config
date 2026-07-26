# Commit Message Format

## Standard Format

```
<Type> #<issue-number>: <Brief description>

<Optional detailed explanation of WHY, not WHAT>
<The code shows WHAT changed>
```

## Commit Types

- **Fix** - Bug fixes that resolve issues
- **Add** - New features or functionality
- **Update** - Enhancements to existing features
- **Refactor** - Code restructuring without behavior change
- **Remove** - Deleting features or code
- **Docs** - Documentation only changes
- **Test** - Adding or updating tests
- **Chore** - Maintenance tasks (dependencies, config, etc.)

## Examples from Real Commits

### Good: Concise with issue reference
```
Fix #70: Use applies_condition field instead of hardcoded string checks

- Add "applies_condition": "on_fire" to alchemists_fire in items.json
- Refactor use_combat_attack_item() to read applies_condition field
- Remove hardcoded "alchemist" string matching

This follows data-driven design principle (ARCHITECTURE.md).
Any item can now apply conditions via JSON without code changes.
```

### Good: Feature addition
```
Add #125: Party management debug commands

Implement /addcharacter and /removecharacter commands for testing:
- Add character to active party from vault
- Remove character from party
- Includes validation and error handling

Useful for testing party-based combat scenarios.
```

### Bad: Vague, no issue reference
```
Update game state

Changed some things in the game state manager
```

### Bad: Too much "what", not enough "why"
```
Fix #123: Change line 45 from if x > 5 to if x >= 5

Modified the comparison operator on line 45 of foo.py
Changed the greater than to greater than or equal
Updated the test to match
```

## Guidelines

1. **Always reference issue number** - Use `Fix #123`, `Add #456`, etc.
2. **Focus on WHY** - The diff shows what changed, explain why it matters
3. **Keep subject line under 72 characters** - Be concise
4. **Use imperative mood** - "Fix bug" not "Fixed bug" or "Fixes bug"
5. **Bullet points for multiple changes** - Use `-` for lists in body
6. **Include Claude attribution** - Always add the footer
7. **One commit per logical change** - Don't bundle unrelated fixes

## Multi-File Changes

When changing multiple files, organize by component:

```
Refactor #89: Extract condition system into separate module

Core changes:
- Move condition logic from game_state.py to condition_manager.py
- Create ConditionManager class with apply/remove/check methods
- Update GameState to use ConditionManager

Tests:
- Add unit tests for ConditionManager
- Update integration tests to use new structure

This improves separation of concerns and makes conditions easier to extend.
```
