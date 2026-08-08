# Pull Request Template

## Standard PR Format

Use this structure when creating pull requests with `gh pr create`:

```markdown
## Summary
<1-3 bullet points describing what changed and why>

## Changes
<Bulleted list of major changes organized by component/file>

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing completed
- [ ] No new warnings or errors

## Related Issues
Fixes #<issue-number>
Related to #<other-issue> (if applicable)
```

## Example PRs

### Feature Addition Example

```markdown
## Summary
- Implement party management debug commands for testing
- Add /addcharacter and /removecharacter commands
- Enables easier testing of party-based combat scenarios

## Changes
- **dnd_engine/ui/debug_console.py**: Add command handlers
  - `cmd_addcharacter`: Select from vault and add to party
  - `cmd_removecharacter`: Select from party and remove
  - Validation for empty vault/party edge cases

- **tests/test_debug_console.py**: Add test coverage
  - Test adding character from vault to party
  - Test removing character from party
  - Test error cases (empty vault, character not found)

## Testing
- [x] Unit tests pass (3 new tests added)
- [x] Integration tests pass
- [x] Manual testing: Successfully added/removed characters in game
- [x] No new warnings or errors

## Related Issues
Fixes #125
```

### Bug Fix Example

```markdown
## Summary
- Fix Alchemist's Fire using hardcoded string checks
- Refactor to use data-driven `applies_condition` field
- Makes system extensible for future condition-applying items

## Changes
- **dnd_engine/data/srd/items.json**: Add `"applies_condition": "on_fire"` field
- **dnd_engine/core/game_state.py**: Replace hardcoded string matching with field lookup
  - Removed `if "alchemist" in item_id.lower()` check
  - Use generic `used_item_data.get("applies_condition")` pattern

## Testing
- [x] Unit tests pass (12/12 on_fire condition tests)
- [x] Integration tests pass (129/129 combat tests)
- [x] Manual testing: Alchemist's Fire still applies on_fire correctly
- [x] No new warnings or errors

## Related Issues
Fixes #70
```

### Refactor Example

```markdown
## Summary
- Extract condition system into separate ConditionManager
- Improve separation of concerns
- Make conditions easier to test and extend

## Changes
- **dnd_engine/systems/condition_manager.py**: New ConditionManager class
  - `apply_condition()`: Apply condition to creature
  - `remove_condition()`: Remove condition from creature
  - `process_turn_effects()`: Handle turn-start/end effects

- **dnd_engine/core/game_state.py**: Refactor to use ConditionManager
  - Replace inline condition logic with manager calls
  - Simplify combat flow by delegating to manager

- **tests/test_condition_manager.py**: New unit tests for ConditionManager
- **tests/test_condition_integration.py**: Update to use new structure

## Testing
- [x] Unit tests pass (15 new tests for ConditionManager)
- [x] Integration tests pass (all existing tests still pass)
- [x] Manual testing: Conditions work identically to before
- [x] No new warnings or errors

## Related Issues
Fixes #89
Related to #122 (conditions system improvements)
```

## PR Best Practices

1. **Reference issue numbers** - Always include `Fixes #123`
2. **Clear summary** - 1-3 bullets covering what and why
3. **Organized changes** - Group by file/component
4. **Complete testing checklist** - Check off all items
5. **Context for reviewers** - Explain non-obvious decisions
6. **Keep PRs focused** - One feature/fix per PR
7. **Update related docs** - Include doc changes in same PR

## Creating PRs with gh CLI

```bash
# Create PR with title and body
gh pr create --title "Fix #70: Use applies_condition field" --body "$(cat <<'EOF'
## Summary
- Brief description here

## Changes
- Change 1
- Change 2

## Testing
- [x] All tests pass

## Related Issues
Fixes #70
EOF
)"
```

## Common Mistakes to Avoid

❌ **Too vague**: "Update code"
✅ **Specific**: "Fix #70: Use applies_condition field instead of hardcoded checks"

❌ **Missing context**: Just listing file changes
✅ **Contextual**: Explaining what changed in each file and why

❌ **Incomplete testing**: Skipping checklist items
✅ **Thorough**: Actually running tests and checking boxes

❌ **No issue reference**: Orphaned PR with no tracking
✅ **Linked**: Clear `Fixes #123` reference
