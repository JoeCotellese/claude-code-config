---
name: python-code-reviewer
description: Perform comprehensive Python code reviews before commits or PRs. Reviews code quality (PEP 8, idioms, DRY, separation of concerns), performance patterns, security vulnerabilities, and best practices for web apps and CLI tools. Uses ruff for linting and formatting checks.
---

# Python Code Reviewer

## Overview

Perform thorough Python code reviews focusing on code quality, security, performance, and best practices. This skill should be invoked before committing Python code or creating pull requests to ensure high-quality, maintainable, and secure code.

## When to Use This Skill

Invoke this skill when:
- User says "let's commit this code" and Python files have been modified
- User says "let's code review this branch" or similar
- User wants to "generate a PR" or "create a pull request" with Python changes
- User explicitly requests a code review with phrases like "review this code" or "check this code"

## Review Workflow

### 1. Identify Changed Files

When triggered, first identify which Python files need review:

```bash
# For uncommitted changes
git diff --name-only --diff-filter=ACMR "*.py"

# For a branch compared to main
git diff --name-only main...HEAD --diff-filter=ACMR "*.py"

# For specific commit
git diff --name-only HEAD~1 HEAD --diff-filter=ACMR "*.py"
```

**Important**: Only review **added, changed, or modified** files (ACMR). Skip deleted files.

### 2. Run Automated Checks

Use the bundled script to run ruff lint and format checks:

```bash
python scripts/run_checks.py <files or directories>
```

Examples:
```bash
# Check all Python files in current directory
python scripts/run_checks.py .

# Check specific files
python scripts/run_checks.py src/main.py src/utils.py

# Check entire src directory
python scripts/run_checks.py src/
```

The script will:
- Run `ruff check` to lint for code quality issues
- Run `ruff format --check` to verify formatting
- Report all issues in a structured format

**If the script reports issues**, inform the user about:
- Number of issues found
- Which files have problems
- Specific error codes and messages from ruff lint
- Which files need formatting by ruff format

**If ruff isn't installed**, suggest:
```bash
pip install ruff
```

### 3. Load Django Design Principles (if applicable)

If the code under review is part of a Django project, read the design principles:

```
Read: ~/.claude/docs/django.md
```

Use these principles as additional review criteria (service layer separation, DRY, composition over inheritance, KISS, etc.) alongside the checks below.

### 4. Manual Code Review

After automated checks, perform manual review of the changed code focusing on:

#### Code Quality & Idioms
- Check `references/python-anti-patterns.md` for common issues:
  - Mutable default arguments
  - Bare exception handling
  - Not using context managers
  - Using `type()` instead of `isinstance()`
  - Not using list/dict/set comprehensions
  - Magic numbers
  - Deep nesting (>3 levels)

- Check `references/code-quality-principles.md` for:
  - **DRY violations**: Duplicated code blocks, repeated logic
  - **Separation of concerns**: Business logic mixed with I/O, multiple responsibilities
  - **Idiomatic Python**: EAFP vs LBYL, context managers, properties
  - **Long string formatting**: Use implicit concatenation for strings exceeding line length
  - **Length violations**:
    - Functions > 50 lines (ideally < 25)
    - Classes > 300 lines (ideally < 200)
    - Files > 500 lines (ideally < 300)
    - Methods with > 5 parameters (ideally < 3)
    - Nesting depth > 3 levels

#### Security Vulnerabilities
Check `references/security-checks.md` for:
- **Injection**: SQL injection, command injection, path traversal, code injection
- **Deserialization**: Unsafe pickle/YAML loading
- **Cryptography**: Weak hashing, hardcoded secrets, insecure random
- **Web vulnerabilities**: XSS, open redirect, missing auth, SSRF
- **Information disclosure**: Verbose errors, logging sensitive data
- **DoS**: ReDoS patterns, unbounded resource consumption

**CRITICAL**: Flag any of these immediately:
- User input in SQL queries (must use parameterized queries)
- `eval()` or `exec()` on untrusted data
- `pickle.loads()` or `yaml.load()` on untrusted data
- Hardcoded API keys, passwords, or secrets
- Missing input validation on user-controlled data
- Command execution with `shell=True` and user input

#### Performance Patterns
Check `references/performance-patterns.md` for:
- List comprehensions vs loops
- Generator expressions for large datasets
- Using appropriate data structures (set vs list for lookups)
- Avoiding repeated attribute lookups
- String concatenation in loops
- Batch database operations (N+1 query problems)
- Caching opportunities with `@lru_cache`

#### Web App / CLI Tool Specific
If the code is a web app or CLI tool, check `references/web-cli-specifics.md` for:

**Web Apps (Flask/FastAPI):**
- Route organization (blueprints/routers)
- Request validation (Pydantic)
- Consistent error handling
- Database session management
- Authentication/authorization
- CORS configuration

**CLI Tools (Click/argparse):**
- Command organization (groups)
- Progress indication for long operations
- Interactive prompts
- Multiple output formats
- Error handling with user-friendly messages
- Configuration file support

### 5. Report Findings

Structure your code review report as follows:

```markdown
## Code Review Results

### Automated Checks
[Summary of ruff results]
- Ruff lint: X issues found
- Ruff format: Y files need formatting

### Manual Review Findings

#### Critical Issues (Must Fix Before Commit)
[Security vulnerabilities, major bugs]

#### Code Quality Issues
[Anti-patterns, DRY violations, separation of concerns]

#### Performance Concerns
[Inefficient algorithms, unnecessary operations]

#### Style & Idioms
[Non-Pythonic code, PEP 8 violations not caught by ruff]

#### Suggestions (Optional Improvements)
[Nice-to-have improvements, refactoring opportunities]

### Summary
[Overall assessment: Ready to commit? Needs changes?]
```

**Severity Levels:**
- **Critical**: Security vulnerabilities, major bugs - MUST fix before commit
- **High**: Code quality issues, performance problems - SHOULD fix before commit
- **Medium**: Style issues, minor anti-patterns - GOOD to fix
- **Low**: Suggestions, optional improvements - NICE to have

### 6. Provide Actionable Feedback

For each issue:
1. **Show the problematic code** with file name and line number
2. **Explain WHY it's an issue** (not just what)
3. **Provide a CONCRETE fix** with code example
4. **Reference the pattern** (e.g., "See python-anti-patterns.md: Mutable Default Arguments")

**Good feedback example:**
```
❌ src/utils.py:15 - Mutable default argument

def add_item(item, items=[]):
    items.append(item)
    return items

ISSUE: Mutable default arguments are shared across all function calls,
leading to unexpected behavior.

FIX:
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

Reference: references/python-anti-patterns.md - Mutable Default Arguments
```

## Decision Tree

```
User triggers code review
    ↓
Identify changed Python files (git diff)
    ↓
Run automated checks (scripts/run_checks.py)
    ↓
Ruff issues found?
    ↓ YES → Report automated issues
    ↓ NO → Continue
    ↓
Django project? → Read ~/.claude/docs/django.md for design principles
    ↓
Perform manual review:
    ↓
1. Check references/python-anti-patterns.md
    ↓
2. Check references/code-quality-principles.md
   - DRY violations?
   - Separation of concerns?
   - Idiomatic Python?
   - Length violations?
    ↓
3. Check references/security-checks.md
   - Injection vulnerabilities?
   - Unsafe deserialization?
   - Hardcoded secrets?
   - Missing validation?
    ↓
4. Check references/performance-patterns.md
   - Inefficient algorithms?
   - Wrong data structures?
   - Missing optimizations?
    ↓
5. If web app or CLI, check references/web-cli-specifics.md
   - Web: Routes, validation, sessions, auth?
   - CLI: Commands, progress, errors, config?
    ↓
Generate structured report with:
   - Automated check results
   - Critical issues (must fix)
   - Code quality issues
   - Performance concerns
   - Style & idioms
   - Suggestions
    ↓
For each issue:
   - Show code + location
   - Explain why it's an issue
   - Provide concrete fix
   - Reference documentation
    ↓
Provide summary assessment:
   ✓ Ready to commit
   ✗ Needs changes (specify what)
```

## Common Review Patterns

### Pattern 1: Pre-Commit Review

```
User: "let's commit this code"
Assistant:
1. Check git status to see which Python files changed
2. Run scripts/run_checks.py on changed files
3. Read the changed Python files
4. Review against references (anti-patterns, security, performance, quality)
5. Generate structured report with findings
6. Provide verdict: Ready to commit or needs changes
```

### Pattern 2: Branch Review

```
User: "let's code review this branch"
Assistant:
1. Get list of changed Python files: git diff main...HEAD
2. Run scripts/run_checks.py on changed files
3. Read each changed file
4. Review systematically through all references
5. Generate comprehensive report organized by severity
6. Provide recommendations for fixes
```

### Pattern 3: PR Preparation

```
User: "generate a PR"
Assistant:
1. Identify Python files changed in branch
2. Run automated checks
3. Perform manual code review
4. If critical issues found:
   - Block PR creation
   - Provide detailed fix recommendations
5. If only minor issues:
   - Note them in PR description
   - Allow PR creation with caveats
6. If no issues:
   - Approve for PR
   - Optionally suggest enhancements in PR description
```

### Pattern 4: Explicit Review Request

```
User: "review this code"
Assistant:
1. Identify scope (single file, directory, or git changes)
2. Run automated checks if applicable
3. Read and review code
4. Focus on areas user mentions if specified
5. Provide detailed feedback with examples
```

## Quick Reference

### Automated Tools

```bash
# Run ruff lint + format checks
python scripts/run_checks.py <path>

# Just lint
ruff check <path>

# Just format check
ruff format --check <path>

# Auto-format
ruff format <path>
```

### Review Checklist

Use this mental checklist during review:

**Code Quality:**
- [ ] No mutable default arguments
- [ ] Context managers for resources
- [ ] No bare exceptions
- [ ] Proper use of isinstance()
- [ ] Pythonic idioms (comprehensions, properties, etc.)
- [ ] No DRY violations
- [ ] Clear separation of concerns
- [ ] Functions < 50 lines
- [ ] Classes < 300 lines
- [ ] Files < 500 lines
- [ ] Long strings use implicit concatenation

**Security:**
- [ ] No SQL injection (parameterized queries only)
- [ ] No command injection (avoid shell=True)
- [ ] No path traversal (validate file paths)
- [ ] No eval/exec on user input
- [ ] No unsafe pickle/YAML loading
- [ ] Secrets in environment variables
- [ ] Using secrets module for tokens
- [ ] Strong password hashing (bcrypt/argon2)
- [ ] Input validation on all user data
- [ ] Authentication on sensitive endpoints

**Performance:**
- [ ] Appropriate data structures
- [ ] Generator expressions for large data
- [ ] No string concatenation in loops
- [ ] Batch database operations
- [ ] Built-in functions used
- [ ] No repeated expensive operations
- [ ] Caching where appropriate

**Web/CLI Specific:**
- [ ] Routes/commands organized
- [ ] Request/input validation
- [ ] Consistent error handling
- [ ] Progress indication (CLI)
- [ ] Configuration file support (CLI)
- [ ] Session management (Web)
- [ ] CORS configured (Web)

## Resources

### scripts/
- `run_checks.py` - Runs ruff lint and format checks, reports issues in structured format

### references/
- `python-anti-patterns.md` - Common anti-patterns with examples and fixes
- `security-checks.md` - Python security vulnerabilities (injection, crypto, web, etc.)
- `performance-patterns.md` - Performance best practices and optimization patterns
- `code-quality-principles.md` - DRY, separation of concerns, idiomatic Python, length limits
- `web-cli-specifics.md` - Best practices for Flask/FastAPI web apps and Click CLI tools

All references contain concrete examples with "bad" and "good" code snippets demonstrating each pattern.