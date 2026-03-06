
# HID Keycodes Reference
This reference provides HID keycodes for use with `axe key` and `axe key-sequence` commands.

## Letters

| Key | Code | Key | Code | Key | Code | Key | Code |
|-----|------|-----|------|-----|------|-----|------|
| a | 4 | h | 11 | o | 18 | v | 25 |
| b | 5 | i | 12 | p | 19 | w | 26 |
| c | 6 | j | 13 | q | 20 | x | 27 |
| d | 7 | k | 14 | r | 21 | y | 28 |
| e | 8 | l | 15 | s | 22 | z | 29 |
| f | 9 | m | 16 | t | 23 | | |
| g | 10 | n | 17 | u | 24 | | |

## Numbers

| Key | Code | Key | Code |
|-----|------|-----|------|
| 1 | 30 | 6 | 35 |
| 2 | 31 | 7 | 36 |
| 3 | 32 | 8 | 37 |
| 4 | 33 | 9 | 38 |
| 5 | 34 | 0 | 39 |

## Special Keys

| Key | Code | Description |
|-----|------|-------------|
| Enter/Return | 40 | Submit forms, confirm actions |
| Escape | 41 | Cancel, dismiss |
| Backspace | 42 | Delete character before cursor |
| Tab | 43 | Move to next field |
| Space | 44 | Space character |
| Minus (-) | 45 | Hyphen/minus |
| Equal (=) | 46 | Equals sign |
| Comma (,) | 54 | Comma |
| Period (.) | 55 | Period/dot |
| Slash (/) | 56 | Forward slash |

## Function Keys

| Key | Code | Key | Code |
|-----|------|-----|------|
| F1 | 58 | F6 | 63 |
| F2 | 59 | F7 | 64 |
| F3 | 60 | F8 | 65 |
| F4 | 61 | F9 | 66 |
| F5 | 62 | F10 | 67 |

## Navigation Keys

| Key | Code | Description |
|-----|------|-------------|
| Right Arrow | 79 | Move cursor right |
| Left Arrow | 80 | Move cursor left |
| Down Arrow | 81 | Move cursor down |
| Up Arrow | 82 | Move cursor up |

## Common Patterns

### Typing "hello"
```bash
axe key-sequence --keycodes 11,8,15,15,18 --udid $UDID
```
Breakdown: h=11, e=8, l=15, l=15, o=18

### Submitting a form (press Enter 3 times)
```bash
axe key-sequence --keycodes 40,40,40 --delay 0.5 --udid $UDID
```

### Tab through fields then submit
```bash
axe key-sequence --keycodes 43,43,43,40 --delay 0.3 --udid $UDID
```
Breakdown: Tab, Tab, Tab, Enter
