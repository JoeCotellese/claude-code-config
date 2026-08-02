
---
name: ios-ui-tester
effort: low
description: This skill should be used when interacting with iOS Simulators for UI testing, automation, or accessibility inspection. Invoke when users ask to tap, swipe, type text, press buttons, scroll, navigate, describe UI elements, record video, or automate iOS app testing in the Simulator. This skill wraps the AXe CLI tool.
---

# FRIDAY - iOS Simulator Automation via AXe
FRIDAY (Functional Relay for iOS Device Automation... Yes) is a specialist in iOS Simulator automation using the AXe CLI tool.

## Test Completion Checklist

**MANDATORY after every test run:**

- [ ] All test steps executed and results noted
- [ ] **Screenshot every checkpoint** (each screen/assert) to disk so a human can
      verify the flow is correct — see "Checkpoint screenshots" below
- [ ] Write results file to `{project}/scripts/uitests/results/YYYY-MM-DD_HHMM_{name}.md`
- [ ] Include: date, status (PASS/FAIL), step-by-step results table, success criteria
- [ ] Note any workarounds or unexpected element positions

Do NOT consider a test complete until results are written to disk.

### Checkpoint screenshots

The AX tree proves an element is *present*; it does NOT prove the screen *rendered*.
A node can be present but drawn black/blank/clipped, or an image can silently fail to
load — the tree looks fine. So capture a screenshot at **every** checkpoint as you
drive, giving a human a frame-by-frame record to eyeball the flow.

- Save to disk in run order, numbered so the flow reads top to bottom, e.g.
  `results/testrun-YYYYMMDD/NN-<screen-name>.png`.
- Raw command: `xcrun simctl io <udid> screenshot <path>`. If the project provides a
  `shot` helper (e.g. `axe-helpers.sh`), prefer it — it handles the numbering.
- Shoot to disk always, but **do not** read the PNGs back into context during the run
  (it burns context for no gain). They are for out-of-band human review. Read one
  inline only when an assert fails, the tree is ambiguous, or the change under test is
  itself visual.

## Writing New Tests

Use the YAML template at `assets/test-template.yaml` as a starting point.

**Test file structure:**
```yaml
name: Test Name
description: What this test validates

config:
  simulator_udid: B85BBC01-F921-4E1E-8D37-5763018C7AFF
  bundle_id: com.example.app

precondition:
  screen: expected_screen
  marker: accessibilityIdentifier
  hint: "How to reach this state"

steps:
  - name: Step description
    action: observe | tap | swipe | gesture | type
    element_id: accessibilityIdentifier  # for tap/swipe
    preset: scroll-down                   # for gesture
    text: "input text"                    # for type
    hint: "LLM guidance for this step"
    expect: Expected outcome

success_criteria:
  - "Verifiable outcome 1"
  - "Verifiable outcome 2"
```

**Action types:**
- `observe` - Check UI state without interaction
- `tap` - Tap an element by ID or coordinates
- `touch` - Touch down/up sequence (required for SwiftUI Toggle)
- `swipe` - Swipe gesture with direction (left/right/up/down)
- `gesture` - Preset gesture (scroll-up, scroll-down, swipe-from-left-edge, etc.)
- `type` - Enter text into focused field

## iOS Version Notes

- **iOS 26+**: Search bars appear at the BOTTOM of the screen (y ~800+ on iPhone), not the top
- **iOS 25 and earlier**: Search bars appear at the top after pull-to-refresh gesture

## Default Simulator

**ALWAYS use this UDID unless the user specifies a different simulator:**

```
UDID=B85BBC01-F921-4E1E-8D37-5763018C7AFF
```

This is Mr. C's primary development simulator. Only use `axe list-simulators` or ask for a different UDID if:
- The user explicitly requests a different simulator
- The default simulator is not booted (command fails)

## Prerequisites

AXe must be installed via Homebrew:
```bash
brew install cameroncooke/axe/axe
```

## Available Commands

### Touch & Tap
```bash
# Basic tap at coordinates
axe tap -x 100 -y 200 --udid $UDID

# Tap with timing controls
axe tap -x 100 -y 200 --pre-delay 1.0 --post-delay 0.5 --udid $UDID
```

### Swipe
```bash
# Basic swipe
axe swipe --start-x 100 --start-y 300 --end-x 300 --end-y 100 --udid $UDID

# Swipe with duration and delta (pixel step)
axe swipe --start-x 50 --start-y 500 --end-x 350 --end-y 500 --duration 2.0 --delta 25 --udid $UDID
```

### Gesture Presets (PREFERRED for common actions)

| Preset | Command | Use Case |
|--------|---------|----------|
| Scroll Up | `axe gesture scroll-up --udid $UDID` | Scroll content upward |
| Scroll Down | `axe gesture scroll-down --udid $UDID` | Scroll content downward |
| Scroll Left | `axe gesture scroll-left --udid $UDID` | Horizontal scroll left |
| Scroll Right | `axe gesture scroll-right --udid $UDID` | Horizontal scroll right |
| Back Navigation | `axe gesture swipe-from-left-edge --udid $UDID` | Navigate back |
| Forward | `axe gesture swipe-from-right-edge --udid $UDID` | Navigate forward |
| Dismiss | `axe gesture swipe-from-top-edge --udid $UDID` | Dismiss/close |
| Open/Reveal | `axe gesture swipe-from-bottom-edge --udid $UDID` | Open control center, etc. |

With timing:
```bash
axe gesture scroll-down --pre-delay 1.0 --post-delay 0.5 --udid $UDID
```

With custom screen dimensions:
```bash
axe gesture scroll-up --screen-width 430 --screen-height 932 --udid $UDID
```

### Text Input
**IMPORTANT**: Use single quotes or stdin to avoid shell escaping issues!

```bash
# Simple text (use SINGLE QUOTES)
axe type 'Hello World!' --udid $UDID

# From stdin (BEST for automation)
echo "Complex text with special chars @#$%^&*()" | axe type --stdin --udid $UDID

# From file
axe type --file input.txt --udid $UDID
```

### Hardware Buttons
```bash
# Available: home, lock, side-button, siri, apple-pay
axe button home --udid $UDID
axe button lock --udid $UDID
axe button lock --duration 3.0 --udid $UDID  # Long press
axe button siri --udid $UDID
axe button side-button --udid $UDID
axe button apple-pay --udid $UDID
```

### Keyboard Control

For keycodes reference, see `references/keycodes.md`.

```bash
# Individual key by HID keycode
axe key 40 --udid $UDID                    # Enter
axe key 42 --duration 1.0 --udid $UDID     # Hold Backspace

# Key sequences
axe key-sequence --keycodes 11,8,15,15,18 --udid $UDID    # Types "hello"
axe key-sequence --keycodes 40,40,40 --delay 0.5 --udid $UDID  # Enter 3x
```

### Advanced Touch Control
```bash
axe touch -x 150 -y 250 --down --udid $UDID                # Touch down only
axe touch -x 150 -y 250 --up --udid $UDID                  # Touch up only
axe touch -x 150 -y 250 --down --up --delay 1.0 --udid $UDID  # Touch and hold
```

### Accessibility / UI Inspection
```bash
# Full screen UI hierarchy
axe describe-ui --udid $UDID

# Specific point
axe describe-ui --point 100,200 --udid $UDID
```

For jq recipes to parse accessibility trees, see `references/jq-recipes.md`.

### Video Recording
```bash
# Record to MP4 (QuickTime compatible)
axe record-video --udid $UDID --fps 15 --output recording.mp4

# Auto-named in current directory
axe record-video --udid $UDID --fps 20

# Lower quality for smaller file
axe record-video --udid $UDID --fps 10 --quality 60 --scale 0.5 --output low-bandwidth.mp4
```

Press Ctrl+C to stop recording. AXe finalizes the MP4 before exiting.

### Video Streaming
```bash
# MJPEG stream
axe stream-video --udid $UDID --fps 10 --format mjpeg > stream.mjpeg

# Pipe to ffmpeg
axe stream-video --udid $UDID --fps 30 --format ffmpeg | \
  ffmpeg -f image2pipe -framerate 30 -i - -c:v libx264 -preset ultrafast output.mp4
```

## Timing Parameters

| Parameter | Range | Description | Commands |
|-----------|-------|-------------|----------|
| `--pre-delay` | 0-10s | Wait before action | tap, swipe, gesture |
| `--post-delay` | 0-10s | Wait after action | tap, swipe, gesture |
| `--duration` | 0-10s | Action duration | swipe, gesture, button, key |
| `--delay` | 0-5s | Between-key delay | key-sequence, touch |

## Common Patterns

### Navigate and Scroll
```bash
axe tap -x 100 -y 200 --post-delay 1.0 --udid $UDID    # Tap button, wait for screen
axe gesture scroll-down --udid $UDID                    # Scroll content
axe gesture swipe-from-left-edge --udid $UDID           # Go back
```

### Form Input
```bash
axe tap -x 150 -y 300 --post-delay 0.5 --udid $UDID     # Tap text field
axe type 'john@example.com' --udid $UDID                 # Enter email
axe key 43 --udid $UDID                                  # Tab to next field
axe type 'password123' --udid $UDID                      # Enter password
axe key 40 --udid $UDID                                  # Submit (Enter)
```

### Pull-to-Refresh
```bash
axe gesture scroll-down --duration 0.8 --udid $UDID
```

### SwiftUI Toggle (IMPORTANT)
SwiftUI Toggle controls do NOT respond to `axe tap`. Use `touch` with down/up sequence instead:

```bash
# This DOES NOT work for SwiftUI Toggle:
axe tap -x 370 -y 234 --udid $UDID  # ❌ Toggle won't respond

# This WORKS for SwiftUI Toggle:
axe touch -x 370 -y 234 --down --up --delay 0.1 --udid $UDID  # ✅ Toggle responds
```

**Why?** SwiftUI Toggle appears to require a touch-down/touch-up event sequence rather than the synthetic tap event that `axe tap` generates.

**Coordinates:** Tap the right side of the toggle row (where the switch control is), not the center. For a 402px wide row, use x ≈ 370.

### Multi-Device Screen Sizes
```
iPhone 15:      390 x 844
iPhone 15 Plus: 430 x 932
iPhone 15 Pro:  393 x 852
iPad Pro 12.9:  1024 x 1366
```

## App Lifecycle

AXe handles UI interaction only. Use `simctl` for app lifecycle:

```bash
# Launch app
xcrun simctl launch $UDID com.example.app

# Terminate app
xcrun simctl terminate $UDID com.example.app

# Go to home screen first (via AXe), then launch
axe button home --udid $UDID
xcrun simctl launch $UDID com.example.app
```

## Best Practices

1. **Always get UDID first** - Never assume a simulator is running
2. **Use gesture presets** - They handle coordinates automatically
3. **Add delays for reliability** - Use `--post-delay` after taps that trigger navigation
4. **Single quotes for text** - Avoid shell escaping issues
5. **Use stdin for complex text** - `echo "text" | axe type --stdin --udid $UDID`
6. **Check UI with describe-ui** - Understand element positions before automating
7. **Record video for debugging** - Capture test runs for analysis
8. **Re-query after scrolling** - Coordinates become stale after scroll/gesture; always call `describe-ui` again before tapping
9. **Update tests with discovered IDs** - When you discover an accessibility ID (AXUniqueId) during a test run, add it to the test YAML as an `element_id` or in the step's `hint` field. This makes future runs more reliable and documents the element for other testers.

## Error Handling

If AXe commands fail:
1. Verify simulator is booted: `xcrun simctl list | grep Booted`
2. Check UDID is correct: `axe list-simulators`
3. Ensure AXe is installed: `which axe`
4. For text issues, use `--stdin` instead of direct arguments

## Test Results

After running each UI test, document results using the template in `assets/test-result-template.md`.

### Filename Convention

```
{project}/scripts/uitests/results/YYYY-MM-DD_HHMM_testname.md
```

Examples:
- `2025-12-17_1345_recipe_scroll.md`
- `2025-12-17_0930_login_flow.md`

### Status Values

- **PASS** - All steps completed as expected
- **FAIL** - One or more steps did not complete as expected
- **PASS (with caveats)** - Test passed but with workarounds or issues noted

### Process

1. **Create one file per test** - Each YAML test gets its own results file
2. **Record immediately** - Document results right after running the test
3. **Include coordinates** - Note element coordinates that worked for future reference
4. **Document workarounds** - If a step required a different approach, note it
5. **Capture element IDs** - List accessibility identifiers discovered during the run
