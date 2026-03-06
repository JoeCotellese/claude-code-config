# Output Components

<!-- ABOUTME: Defines reusable visual components for terminal output formatting. -->
<!-- ABOUTME: Provides a design system for consistent, scannable productivity skill responses. -->

## Design Principles

1. **Scannable** — Users should grasp the key information in 2-3 seconds
2. **Aligned** — Columns align for easy comparison; metadata doesn't clutter descriptions
3. **Hierarchical** — Clear visual distinction between headers, content, and actions
4. **Compact** — Respect terminal real estate; no unnecessary blank lines
5. **Accessible** — Works in any terminal; no color dependencies

---

## Icon Legend

Use these unicode symbols consistently throughout output:

### Energy Levels
| Icon | Label | When to Use |
|------|-------|-------------|
| `⚡` | High | Deep work, creative, strategic thinking |
| `◐` | Medium | Routine work, meetings, planning |
| `○` | Low | Admin, simple lookups, errands |

### Task Status
| Icon | Meaning |
|------|---------|
| `☐` | Pending / To do |
| `✓` | Completed |
| `⏳` | Waiting / Blocked |
| `→` | Delegated |
| `✕` | Cancelled / Removed |

### Time Blocks
| Icon | Meaning |
|------|---------|
| `●` | Busy / Meeting |
| `○` | Free / Available |
| `◐` | Partially available |
| `░` | Buffer / Transition |

### Context (optional, use sparingly)
| Icon | Context |
|------|---------|
| `💻` | @computer |
| `📱` | @phone |
| `🏠` | @home |
| `🏢` | @work |
| `🚗` | @errands |
| `📍` | @anywhere |

> **Note:** Context icons are optional. When space is tight, use text labels instead.

---

## Components

### Section Header

Use for major sections of output. Creates clear visual breaks.

```
┌─────────────────────────────────────────────────────────────┐
│  {ICON} {TITLE}                                             │
└─────────────────────────────────────────────────────────────┘
```

**Examples:**
```
┌─────────────────────────────────────────────────────────────┐
│  📅 YOUR DAY: Tuesday, March 6                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📥 INBOX PROCESSING                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ✓ TASK COMPLETE                                            │
└─────────────────────────────────────────────────────────────┘
```

---

### Subsection Header

Use for groupings within a section. Lighter weight than section header.

```
── {TITLE} ──────────────────────────────────────────────────
```

**Examples:**
```
── Morning ──────────────────────────────────────────────────

── Suggested Tasks ──────────────────────────────────────────

── Waiting For ──────────────────────────────────────────────
```

---

### Task List

Aligned table format for task listings. Columns: number, description, energy, time, context.

```
  # │ Description                          Energy  Time   Context
 ───┼────────────────────────────────────────────────────────────
  1 │ {task description}                      ⚡    30m   @computer
  2 │ {task description}                      ◐    15m   @phone
  3 │ {task description}                      ○     5m   @errands
```

**Compact variant** (no header row, for shorter lists):
```
  1 │ Review pull request                     ○    15m   @computer
  2 │ Create project reference file           ◐    15m   @computer
  3 │ Look up definition                      ○     5m   @computer
```

**With recommendation:**
```
  1 │ Review pull request                     ○    15m   @computer
  2 │ Create project reference file           ◐    15m   @computer
  3 │ Look up definition                      ○     5m   @computer

  ▸ Recommendation: #1 — fits your time and energy
```

---

### Daily Schedule

Timeline view of the day with free blocks and meetings.

```
  Time          Event                              Status
 ─────────────────────────────────────────────────────────
  8:00 -  9:00  ○ FREE (1h)
  9:00 - 10:00  ● Team standup
 10:00 - 12:00  ○ FREE (2h)                        ★ Deep work
 12:00 -  1:00  ░ Lunch
  1:00 -  2:00  ○ FREE (1h)
  2:00 -  3:00  ● Client call
  3:00 -  5:00  ○ FREE (2h)
```

**Compact timeline** (visual overview):
```
  8   9  10  11  12   1   2   3   4   5
  ○───●───○───○───░───○───●───○───○───○

  ● Busy   ○ Free   ░ Buffer

  Free: 6h total │ Morning: 3h │ Afternoon: 3h
```

---

### Schedule Slot with Suggestion

When showing a free block with a task suggestion:

```
  10:00 - 12:00  ○ FREE (2h) ★ Deep work
                 ▸ Suggested: Write API documentation  ⚡ 1h
```

---

### Progress Indicator

Use during multi-item processing (inbox, batch operations).

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [3/12]
```

**With percentage bar:**
```
  Processing inbox...  [████████░░░░░░░░░░░░]  40%  (8 of 20)
```

**Simple counter:**
```
  [3 of 12]
```

---

### Inbox Item Card

For processing individual inbox items:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [3/12]

  Original:  "Kids sketcher socks"

  Rewrite:   "Buy Kids Skechers socks"
             └─ Added verb, fixed spelling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [k]eep rewrite  │  [e]dit  │  [d]elete  │  [s]kip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Project Card

Compact summary of a project's status:

```
┌─ PROJECT ───────────────────────────────────────────────────┐
│  NEXTGRES Analytics                                         │
│                                                             │
│  Status: Active              Due: March 15                  │
│  Next:   Write API docs      Waiting: 2 items               │
│                                                             │
│  📄 obsidian://open?vault=obsidian-vault&file=4_Projects... │
└─────────────────────────────────────────────────────────────┘
```

**Minimal variant:**
```
  ┌─ NEXTGRES Analytics ──────────────────────────────────────┐
  │  Next: Write API docs  │  Waiting: 2  │  Due: Mar 15      │
  └───────────────────────────────────────────────────────────┘
```

---

### Action Footer

Show available commands at the bottom of interactive output:

```
─────────────────────────────────────────────────────────────
  [1-3] Select  │  [n]ext  │  [s]kip  │  [?] help  │  [q]uit
```

**Contextual variants:**
```
─────────────────────────────────────────────────────────────
  [y]es  │  [n]o  │  [e]dit  │  [s]kip
```

```
─────────────────────────────────────────────────────────────
  [k]eep  │  [d]elete  │  [s]omeday  │  [p]roject
```

---

### Summary Statistics

For end-of-workflow summaries:

```
── Summary ──────────────────────────────────────────────────

  Processed:  12 items
  ✓ Kept:      5 → Next Actions
  → Moved:     3 → Someday/Maybe
  ✕ Deleted:   4

  Inbox: 0 items remaining ✓
```

---

### Confirmation Message

For successful operations:

```
  ✓ Task completed: "Review pull request"
```

```
  ✓ Added to Next Actions: "Write API documentation"
    └─ ⚡ high  │  1h  │  @computer
```

---

### Warning / Attention

When something needs user attention:

```
  ⚠ No tasks match your current filters
    └─ Try: relaxing energy (◐ → ○) or expanding time
```

```
  ⚠ Calendar unavailable — using manual time estimate
```

---

### Recommendation Callout

Highlight a specific recommendation:

```
  ╭─────────────────────────────────────────────────────────╮
  │  ▸ Recommendation: Start with "Review pull request"     │
  │    Fits your 45-minute window and low energy level      │
  ╰─────────────────────────────────────────────────────────╯
```

---

## Composition Examples

### Example: "What's my day look like?"

```
┌─────────────────────────────────────────────────────────────┐
│  📅 YOUR DAY: Tuesday, March 6                              │
└─────────────────────────────────────────────────────────────┘

  Time          Event
 ─────────────────────────────────────────────────────────────
  8:00 -  9:00  ○ FREE (1h)
                ▸ Create project reference file     ◐  15m

  9:00 - 10:00  ● Team standup

 10:00 - 12:00  ○ FREE (2h)                        ★ Deep work
                ▸ Write API documentation           ⚡  1h

 12:00 -  1:00  ░ Lunch

  1:00 -  2:00  ○ FREE (1h)
                ▸ Call mom                          ○  15m

  2:00 -  3:00  ● Client call

  3:00 -  5:00  ○ FREE (2h)

── Summary ──────────────────────────────────────────────────

  Free: 6h total  │  Meetings: 2  │  Deep work slot: 10am-12pm

─────────────────────────────────────────────────────────────
  [1-3] Start task  │  [m]ore suggestions  │  [d]one
```

---

### Example: Inbox Processing

```
┌─────────────────────────────────────────────────────────────┐
│  📥 INBOX PROCESSING                                        │
└─────────────────────────────────────────────────────────────┘

  Found 12 items in your inbox. Let's process them.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  [1/12]

  Original:  "Kids sketcher socks"

  Rewrite:   "Buy Kids Skechers socks"
             └─ Added verb, fixed spelling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [k]eep rewrite  │  [e]dit  │  [d]elete  │  [s]kip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Example: Task Suggestions

```
┌─────────────────────────────────────────────────────────────┐
│  📋 SUGGESTED TASKS                                         │
└─────────────────────────────────────────────────────────────┘

  You have 45 minutes before your 2pm meeting.
  Context: @computer  │  Energy: low

  1 │ Review pull request                     ○    15m   @computer
  2 │ Create project reference file           ◐    15m   @computer
  3 │ Look up definition                      ○     5m   @computer

  ╭─────────────────────────────────────────────────────────╮
  │  ▸ Recommendation: #1 — good fit for time and energy    │
  ╰─────────────────────────────────────────────────────────╯

─────────────────────────────────────────────────────────────
  [1-3] Start task  │  [m]ore options  │  [s]kip
```

---

## Usage Notes

1. **Don't overuse boxes** — Reserve `┌───┐` headers for major sections only
2. **Align columns** — Use fixed-width formatting for task lists
3. **Progressive disclosure** — Show summary first, details on request
4. **Respect terminal width** — Keep lines under 70 characters when possible
5. **Test in monospace** — These components assume monospace font rendering
