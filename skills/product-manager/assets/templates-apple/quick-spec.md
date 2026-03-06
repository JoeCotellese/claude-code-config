
# Quick Spec Template - Apple Platforms
**Use for**: Single-interaction features, obvious UX, low risk. If you're debating whether
this needs a full brief, it probably doesn't.

---

## [Feature Name]

**What**: [One sentence — what does the user do and what happens?]

**Why**: [One sentence — what user problem does this solve?]

**Acceptance Criteria**:
- [ ] [Core behavior works]
- [ ] [Edge case handled]
- [ ] [Error state handled]

**Analytics**: `event_name` — [when it fires]

**Accessibility**:
- [ ] VoiceOver label: "[label]"
- [ ] Tap target: 44x44pt minimum
- [ ] Dynamic Type: Scales with system settings

---

## Examples

### Example 1: Quick Action - Last Recipe

**What**: Long press app icon to open the last viewed recipe.

**Why**: Power users want faster access to recipes they're actively cooking.

**Acceptance Criteria**:
- [ ] "Last Recipe" quick action appears when user has viewed a recipe this session
- [ ] Tapping opens that recipe directly (skips list view)
- [ ] If recipe was deleted, shows brief error and opens recipe list instead

**Analytics**: `quick_action_used` with `type: "last_recipe"`

**Accessibility**:
- [ ] VoiceOver label: "Last Recipe, [Recipe Name]"
- [ ] Quick action available via VoiceOver custom actions
- [ ] Works with Voice Control: "Tap Last Recipe"

---

### Example 2: Copy Recipe Link

**What**: Tap share icon → "Copy Link" copies recipe URL to clipboard.

**Why**: Users want to quickly paste recipe links into messages without opening share sheet.

**Acceptance Criteria**:
- [ ] "Copy Link" option in share menu
- [ ] Shows "Copied!" confirmation toast
- [ ] Works offline (uses cached URL)

**Analytics**: `recipe_shared` with `method: "copy_link"`

**Accessibility**:
- [ ] VoiceOver announces "Copied to clipboard" on success
- [ ] Confirmation toast respects Reduce Motion (no slide animation)

---

### Example 3: Pull to Refresh

**What**: Pull down on recipe list to refresh from server.

**Why**: Users expect this standard iOS pattern; currently no way to manually refresh.

**Acceptance Criteria**:
- [ ] Standard iOS pull-to-refresh animation
- [ ] Fetches latest recipes from server
- [ ] Shows error toast if offline (keeps existing data)

**Analytics**: `recipe_list_refreshed` with `source: "pull_to_refresh"`

**Accessibility**:
- [ ] VoiceOver announces "Refreshing" when initiated
- [ ] VoiceOver announces "Refresh complete" or error message
- [ ] Works with Switch Control (accessible via actions menu)

---

### Example 4: Widget Quick Add

**What**: Tap "+" on Home Screen widget to add new recipe.

**Why**: Reduce friction for capturing recipe ideas.

**Acceptance Criteria**:
- [ ] Widget displays "+" button in corner
- [ ] Tapping opens app to new recipe screen
- [ ] Deep link preserves widget context

**Analytics**: `widget_action_tapped` with `action: "add_recipe"`

**Accessibility**:
- [ ] Widget "+" has VoiceOver label "Add new recipe"
- [ ] Dynamic Type: Widget text scales appropriately
