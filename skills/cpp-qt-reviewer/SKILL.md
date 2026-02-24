---
name: cpp-qt-reviewer
description: "Perform comprehensive C++/Qt code reviews before commits or PRs. Reviews memory safety (RAII, ownership, smart pointers), Qt-specific pitfalls (parent-child ownership, signal/slot thread safety), modern C++ idioms (C++17/20), concurrency, security, and performance. Uses clang-format, clang-tidy, and clazy for automated checks."
---

# C++/Qt Code Reviewer

## Overview

Perform thorough C++ and Qt code reviews focusing on memory safety, ownership, modern idioms, concurrency, security, and performance. This skill should be invoked before committing C++/Qt code or creating pull requests. Designed to catch the bugs that matter most in C++ — the ones that compile fine but blow up at runtime.

## When to Use This Skill

Invoke this skill when:
- User says "let's commit this code" and C++ files have been modified
- User says "let's code review this branch" or similar
- User wants to "generate a PR" or "create a pull request" with C++ changes
- User explicitly requests a code review with phrases like "review this code" or "check this code"

## Review Workflow

### Step 1: Identify Changed Files

When triggered, first identify which C++ files need review:

```bash
# For uncommitted changes
git diff --name-only --diff-filter=ACMR -- '*.cpp' '*.h' '*.hpp' '*.cxx' '*.cc' '*.hxx'

# For a branch compared to main
git diff --name-only main...HEAD --diff-filter=ACMR -- '*.cpp' '*.h' '*.hpp' '*.cxx' '*.cc' '*.hxx'
```

**Important**: Only review **added, changed, or modified** files (ACMR). Skip deleted files.

### Step 2: Run Automated Checks

Use the bundled script to run clang-format, clang-tidy, and clazy:

```bash
bash scripts/run_checks.sh <file1.cpp> <file2.h> ...
```

The script will:
- Run `clang-format --dry-run -Werror` to check formatting
- Run `clang-tidy` if `compile_commands.json` is available
- Run `clazy-standalone` if installed and `compile_commands.json` is available
- Run `cppcheck` as a supplementary check if installed
- Report all issues in a structured format
- Gracefully skip tools that aren't installed

**If the script reports issues**, inform the user about:
- Number of issues found per tool
- Which files have problems
- Specific warnings and error codes
- Whether `compile_commands.json` is missing (limits clang-tidy/clazy effectiveness)

**If tools aren't installed**, suggest:
```bash
# macOS
brew install llvm clazy cppcheck

# Ubuntu/Debian
sudo apt install clang-format clang-tidy clazy cppcheck

# Arch
sudo pacman -S clang clazy cppcheck
```

### Step 3: Manual Code Review

After automated checks, perform manual review of the changed code focusing on the categories below. Load the relevant reference file for each category as needed.

#### 3.1 Memory Safety & Ownership
Load: `references/memory-safety.md`

- RAII for all resource management (no manual new/delete)
- Smart pointer selection (unique_ptr vs shared_ptr vs QPointer)
- Qt parent-child ownership used correctly
- No mixing of Qt ownership and std smart pointers on same object
- Virtual destructors on base classes
- No dangling pointers or references
- Move semantics used where appropriate

#### 3.2 Modern C++ Idioms
Load: `references/cpp-anti-patterns.md`

- C++17 features used where appropriate (structured bindings, std::optional, if-init)
- No C-style casts (use static_cast, dynamic_cast, etc.)
- No raw arrays (use std::array, std::vector, QVector)
- No C-style strings for logic (use std::string or QString)
- Range-based for loops
- auto used judiciously (not excessively)
- Const correctness throughout
- Rule of zero preferred (Rule of five when needed)
- No implicit conversions that hide intent

#### 3.3 Qt-Specific Patterns
Load: `references/qt-pitfalls.md`

- Q_OBJECT macro present on all QObject subclasses with signals/slots
- Signal/slot connection type correct for threading context
- No blocking the event loop (long operations offloaded to threads)
- QString::arg() preferred over concatenation
- Proper use of QPointer for guarded pointers
- Q_PROPERTY for QML-exposed properties
- Event filter patterns correct
- QTimer::singleShot for deferred execution

#### 3.4 Concurrency & Thread Safety
Load: `references/concurrency.md`

- Data races identified (shared mutable state without synchronization)
- Mutex usage correct (lock_guard, unique_lock, scoped_lock)
- No potential deadlocks (consistent lock ordering)
- moveToThread pattern correct for Qt threading
- Signal/slot connections across threads use Qt::QueuedConnection
- No shared_ptr across thread boundaries without synchronization
- Atomic types for simple shared flags

#### 3.5 Security
Load: `references/security-checks.md`

- No buffer overflows (bounds checking, safe string functions)
- No integer overflow in arithmetic (especially size calculations)
- No format string vulnerabilities
- No command injection via system() or QProcess with unsanitized input
- No use-after-free patterns
- Input validation on external data (network, file, user input)
- No hardcoded credentials or secrets

#### 3.6 Performance
Load: `references/performance-patterns.md`

- Pass by const reference for non-trivial types
- Move semantics for temporaries and returns
- Container pre-allocation (reserve)
- No unnecessary copies (especially in loops)
- QString built efficiently (arg, QStringBuilder)
- Appropriate container choice (QHash vs QMap, QVector vs QList)
- No virtual calls in hot loops without justification
- Avoid repeated QObject::findChild lookups

#### 3.7 Code Quality & Structure

- **Length limits**:
  - Functions: ideally < 40 lines, hard limit 80
  - Classes: ideally < 300 lines, hard limit 500
  - Files: ideally < 500 lines, hard limit 800
  - Function parameters: ideally < 4, hard limit 6
  - Nesting depth: max 3 levels
- **Header hygiene**: Include guards or #pragma once, minimal includes, forward declarations
- **Naming conventions**: Consistent with project style (Qt convention: camelCase methods, PascalCase classes)
- **DRY**: No duplicated logic
- **Separation of concerns**: UI separate from business logic
- **ABOUTME comments**: All source files start with 2-line ABOUTME comment

### Step 4: Report Findings

Structure your code review report as follows:

```markdown
## Code Review Results

### Automated Checks
[Summary of tool results]
- clang-format: X files need formatting
- clang-tidy: Y warnings found
- clazy: Z Qt-specific issues found
- cppcheck: W issues found

### Manual Review Findings

#### Critical Issues (Must Fix Before Commit)
[Memory safety, security vulnerabilities, data races, undefined behavior]

#### Code Quality Issues
[Anti-patterns, ownership confusion, missing RAII, const correctness]

#### Performance Concerns
[Unnecessary copies, wrong container, missing reserves]

#### Style & Idioms
[Non-modern C++, Qt anti-patterns, naming issues]

#### Suggestions (Optional Improvements)
[Nice-to-have improvements, refactoring opportunities]

### What's Good
[Highlight patterns done well — positive reinforcement]

### Summary
[Overall assessment: Ready to commit? Needs changes?]
```

**Severity Levels:**
- **Critical**: Memory bugs, security issues, data races, UB — MUST fix before commit
- **High**: Ownership confusion, missing RAII, const correctness — SHOULD fix before commit
- **Medium**: Style issues, minor anti-patterns, naming — GOOD to fix
- **Low**: Suggestions, optional improvements — NICE to have

### Step 5: Provide Actionable Feedback

For each issue:
1. **Show the problematic code** with file name and line number
2. **Explain WHY it's an issue** (educational — what could go wrong at runtime?)
3. **Provide a CONCRETE fix** with code example
4. **Reference the pattern** (e.g., "See references/memory-safety.md: Smart Pointer Selection")

**Good feedback example:**
```
❌ src/DeviceController.cpp:42 — Raw owning pointer without RAII

    Widget* panel = new StatusPanel();
    // ... 30 lines of code ...
    delete panel;

ISSUE: If any code between new and delete throws an exception or returns
early, the memory leaks. Manual new/delete is the #1 source of memory
bugs in C++.

FIX:
    auto panel = std::make_unique<StatusPanel>();
    // ... panel automatically deleted when scope exits ...

If this widget needs Qt parent-child ownership instead:
    auto* panel = new StatusPanel(this);  // 'this' takes ownership
    // No delete needed — Qt parent will delete it

Reference: references/memory-safety.md — RAII and Smart Pointers
```

## Decision Tree

```
User triggers code review
    ↓
Identify changed C++/Qt files (git diff)
    ↓
Run automated checks (scripts/run_checks.sh)
    ↓
clang-format issues found?
    ↓ YES → Report formatting issues
    ↓ NO → Continue
    ↓
clang-tidy/clazy/cppcheck issues found?
    ↓ YES → Report and categorize by severity
    ↓ NO → Continue
    ↓
Perform manual review:
    ↓
1. Check references/memory-safety.md
   - Raw new/delete?
   - Smart pointer misuse?
   - Qt ownership conflicts?
   - Dangling references?
    ↓
2. Check references/cpp-anti-patterns.md
   - C-style casts?
   - Missing const?
   - Old-style C++?
   - Rule of five violations?
    ↓
3. Check references/qt-pitfalls.md
   - Missing Q_OBJECT?
   - Event loop blocking?
   - Wrong connection type?
   - QString misuse?
    ↓
4. Check references/concurrency.md
   - Data races?
   - Missing locks?
   - Deadlock potential?
   - Thread-unsafe signal/slot?
    ↓
5. Check references/security-checks.md
   - Buffer overflow?
   - Integer overflow?
   - Command injection?
   - Unvalidated input?
    ↓
6. Check references/performance-patterns.md
   - Unnecessary copies?
   - Wrong containers?
   - Missing reserves?
   - Hot-path inefficiency?
    ↓
Generate structured report with:
   - Automated check results
   - Critical issues (must fix)
   - Code quality issues
   - Performance concerns
   - Style & idioms
   - What's good (positive reinforcement)
   - Suggestions
    ↓
For each issue:
   - Show code + location
   - Explain why it's dangerous
   - Provide concrete fix
   - Reference documentation
    ↓
Provide summary assessment:
   ✓ Ready to commit
   ✗ Needs changes (specify what)
```

## Suggesting Sanitizer Usage

When reviewing code that involves:
- **Pointer arithmetic or raw memory** → suggest AddressSanitizer (ASan)
- **Integer arithmetic or type conversions** → suggest UndefinedBehaviorSanitizer (UBSan)
- **Multi-threaded code** → suggest ThreadSanitizer (TSan)

Provide the compiler flags:
```bash
# AddressSanitizer
CXXFLAGS="-fsanitize=address -fno-omit-frame-pointer -g"

# UndefinedBehaviorSanitizer
CXXFLAGS="-fsanitize=undefined -g"

# ThreadSanitizer
CXXFLAGS="-fsanitize=thread -g"

# Combined (ASan + UBSan — cannot combine ASan with TSan)
CXXFLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer -g"
```

## Resources

### scripts/
- `run_checks.sh` — Runs clang-format, clang-tidy, clazy, and cppcheck with graceful fallback

### references/
- `memory-safety.md` — RAII, smart pointers, ownership, Qt parent-child, Rule of Zero/Five
- `cpp-anti-patterns.md` — Common C++ mistakes with examples and fixes
- `security-checks.md` — Buffer overflow, integer overflow, injection, format strings
- `performance-patterns.md` — Copies, moves, containers, reserves, hot-path optimization
- `qt-pitfalls.md` — Qt-specific issues (Q_OBJECT, signal/slot threading, event loop, QString)
- `concurrency.md` — Data races, mutexes, deadlocks, Qt threading patterns

All references contain concrete "bad" and "good" code snippets.
