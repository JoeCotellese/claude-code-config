# ABOUTME: jq recipes for parsing iOS accessibility tree output from describe_ui
# ABOUTME: Provides patterns for extracting elements, coordinates, and screen fingerprints

# jq Recipes for Accessibility Trees

Patterns for parsing `describe_ui` / `axe describe-ui` JSON output.

## Setup

Save accessibility tree to temp file first:
```bash
axe describe-ui --udid $UDID > /tmp/ui.json 2>/dev/null
```

Or with MCP, save the `describe_ui` result to `/tmp/ui.json`.

**Why save to file?** AXe emits an `objc[...]` warning to stderr that interferes with piping directly to jq. Redirecting stderr with `2>/dev/null` while piping is unreliable. The save-then-query pattern is consistently reliable.

## Recipes

### Compact Screen Summary
All interactable elements with tap coordinates:
```bash
jq '[.. | objects | select(.type == "Button" or .type == "TextField") | {type, id: .AXUniqueId, label: (.AXLabel // .AXValue), x: (.frame.x + .frame.width/2 | floor), y: (.frame.y + .frame.height/2 | floor)}]' /tmp/ui.json
```

### Find Element by Accessibility ID
Get coordinates for a specific element:
```bash
jq '.. | objects | select(.AXUniqueId == "loginButton") | {id: .AXUniqueId, label: .AXLabel, x: (.frame.x + .frame.width/2 | floor), y: (.frame.y + .frame.height/2 | floor)}' /tmp/ui.json
```

### Ready-to-Tap Coordinates
Output just "x y" for piping to tap command:
```bash
jq -r '.. | objects | select(.AXUniqueId == "loginButton") | "\(.frame.x + .frame.width/2 | floor) \(.frame.y + .frame.height/2 | floor)"' /tmp/ui.json
```

### All Buttons
List all buttons with labels and coordinates:
```bash
jq '[.. | objects | select(.type == "Button") | {id: .AXUniqueId, label: .AXLabel, x: (.frame.x + .frame.width/2 | floor), y: (.frame.y + .frame.height/2 | floor)}]' /tmp/ui.json
```

### All Text Fields
List text fields with placeholder text and secure flag:
```bash
jq '[.. | objects | select(.type == "TextField") | {id: .AXUniqueId, placeholder: .AXValue, secure: (.subrole == "AXSecureTextField"), x: (.frame.x + .frame.width/2 | floor), y: (.frame.y + .frame.height/2 | floor)}]' /tmp/ui.json
```

### All Accessibility IDs
Quick list of all IDs on screen:
```bash
jq '[.. | objects | .AXUniqueId | select(type == "string")] | unique' /tmp/ui.json
```

### Screen Fingerprint
All labels/values (useful for identifying screens):
```bash
jq '[.. | objects | (.AXLabel // .AXValue) | select(type == "string")] | unique' /tmp/ui.json
```

### Element Count by Type
Overview of element types on screen:
```bash
jq '[.. | objects | .type | select(type == "string")] | group_by(.) | map({type: .[0], count: length}) | sort_by(-.count)' /tmp/ui.json
```

## Notes

- All recipes use `.. | objects` for recursive descent through nested children
- Coordinates are calculated as center point: `x + width/2, y + height/2`
- Use `| floor` to get integer coordinates suitable for tap commands
- Use `select(type == "string")` instead of `!= null` to avoid shell escaping issues with `!`
