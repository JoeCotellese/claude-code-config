#!/usr/bin/env bash
# ABOUTME: Automated C++/Qt code quality checker for the cpp-qt-reviewer skill.
# ABOUTME: Runs clang-format, clang-tidy, clazy, and cppcheck with graceful fallback.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Counters
TOTAL_ISSUES=0
FORMAT_ISSUES=0
TIDY_ISSUES=0
CLAZY_ISSUES=0
CPPCHECK_ISSUES=0
TOOLS_MISSING=()

usage() {
    echo "Usage: $0 <file1.cpp> [file2.h] [file3.cpp] ..."
    echo ""
    echo "Runs C++/Qt code quality checks on specified files."
    echo ""
    echo "Tools checked (in order):"
    echo "  1. clang-format  — Code formatting"
    echo "  2. clang-tidy    — General C++ static analysis (needs compile_commands.json)"
    echo "  3. clazy          — Qt-specific static analysis (needs compile_commands.json)"
    echo "  4. cppcheck      — Supplementary bug finding"
    echo ""
    echo "Missing tools are skipped with a warning."
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

# Collect files, filtering to only C++ source/header files that exist
FILES=()
for arg in "$@"; do
    if [[ "$arg" =~ \.(cpp|h|hpp|cxx|cc|hxx)$ ]] && [ -f "$arg" ]; then
        FILES+=("$arg")
    fi
done

if [ ${#FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}No C++ files found in arguments.${NC}"
    exit 0
fi

echo -e "${BOLD}C++/Qt Code Quality Check${NC}"
echo -e "Files to check: ${#FILES[@]}"
echo "────────────────────────────────────────"

# --- Project Configuration Checks ---

echo ""
echo -e "${BOLD}[Project Config]${NC}"

# Check for .clang-format
CLANG_FORMAT_CONFIG=""
SEARCH_DIR="$(pwd)"
while [ "$SEARCH_DIR" != "/" ]; do
    if [ -f "$SEARCH_DIR/.clang-format" ] || [ -f "$SEARCH_DIR/_clang-format" ]; then
        CLANG_FORMAT_CONFIG="$SEARCH_DIR/.clang-format"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -n "$CLANG_FORMAT_CONFIG" ]; then
    echo -e "  ${GREEN}✓${NC} .clang-format found: $CLANG_FORMAT_CONFIG"
else
    echo -e "  ${YELLOW}⚠${NC} No .clang-format found in project hierarchy."
    echo -e "    ${BLUE}Suggestion:${NC} Create one for consistent formatting across the team."
    echo -e "    Quick start options:"
    echo -e "      clang-format -style=llvm -dump-config > .clang-format    # LLVM style"
    echo -e "      clang-format -style=google -dump-config > .clang-format  # Google style"
    echo -e "      clang-format -style=webkit -dump-config > .clang-format  # WebKit style (Qt-friendly)"
    echo -e "    Then customize BasedOnStyle, IndentWidth, ColumnLimit, etc. to taste."
fi

# Check for compile_commands.json
COMPILE_COMMANDS=""
SEARCH_DIR="$(pwd)"
while [ "$SEARCH_DIR" != "/" ]; do
    if [ -f "$SEARCH_DIR/compile_commands.json" ]; then
        COMPILE_COMMANDS="$SEARCH_DIR/compile_commands.json"
        break
    fi
    # Also check build/ subdirectory
    if [ -f "$SEARCH_DIR/build/compile_commands.json" ]; then
        COMPILE_COMMANDS="$SEARCH_DIR/build/compile_commands.json"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -n "$COMPILE_COMMANDS" ]; then
    echo -e "  ${GREEN}✓${NC} compile_commands.json found: $COMPILE_COMMANDS"
    COMPILE_DB_DIR="$(dirname "$COMPILE_COMMANDS")"
else
    echo -e "  ${YELLOW}⚠${NC} No compile_commands.json found."
    echo -e "    clang-tidy and clazy need this for accurate analysis."
    echo -e "    ${BLUE}To generate:${NC}"
    echo -e "      CMake:  cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build"
    echo -e "      qmake:  Use Bear — bear -- make"
    echo -e "      Make:   Use Bear — bear -- make"
    echo -e "    Without it, clang-tidy/clazy will run with limited accuracy."
fi

echo ""

# --- 1. clang-format ---

echo -e "${BOLD}[1/4] clang-format${NC} — Formatting"

if command -v clang-format &>/dev/null; then
    FORMAT_OUTPUT=""
    for f in "${FILES[@]}"; do
        # --dry-run -Werror exits non-zero if formatting needed
        if ! result=$(clang-format --dry-run -Werror "$f" 2>&1); then
            FORMAT_OUTPUT+="$result"$'\n'
            ((FORMAT_ISSUES++)) || true
        fi
    done

    if [ $FORMAT_ISSUES -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} All files correctly formatted."
    else
        echo -e "  ${RED}✗${NC} $FORMAT_ISSUES file(s) need formatting:"
        echo "$FORMAT_OUTPUT" | head -50
        echo ""
        echo -e "  ${BLUE}Auto-fix:${NC} clang-format -i ${FILES[*]}"
        TOTAL_ISSUES=$((TOTAL_ISSUES + FORMAT_ISSUES))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} clang-format not installed. Skipping."
    TOOLS_MISSING+=("clang-format")
fi

echo ""

# --- 2. clang-tidy ---

echo -e "${BOLD}[2/4] clang-tidy${NC} — C++ Static Analysis"

if command -v clang-tidy &>/dev/null; then
    TIDY_OUTPUT=""
    TIDY_ARGS=()

    if [ -n "$COMPILE_COMMANDS" ]; then
        TIDY_ARGS+=("-p" "$COMPILE_DB_DIR")
    fi

    for f in "${FILES[@]}"; do
        result=$(clang-tidy "${TIDY_ARGS[@]}" "$f" 2>&1) || true
        # Count warnings (lines matching "warning:" or "error:")
        warnings=$(echo "$result" | grep -cE "(warning|error):" 2>/dev/null) || warnings=0
        if [ "$warnings" -gt 0 ]; then
            TIDY_OUTPUT+="$result"$'\n'
            TIDY_ISSUES=$((TIDY_ISSUES + warnings))
        fi
    done

    if [ $TIDY_ISSUES -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} No issues found."
    else
        echo -e "  ${RED}✗${NC} $TIDY_ISSUES warning(s) found:"
        echo "$TIDY_OUTPUT" | grep -E "(warning|error):" | head -30
        if [ $TIDY_ISSUES -gt 30 ]; then
            echo -e "  ... and $((TIDY_ISSUES - 30)) more"
        fi
        TOTAL_ISSUES=$((TOTAL_ISSUES + TIDY_ISSUES))
    fi

    if [ -z "$COMPILE_COMMANDS" ]; then
        echo -e "  ${YELLOW}Note:${NC} Running without compile_commands.json — results may be incomplete."
    fi
else
    echo -e "  ${YELLOW}⚠${NC} clang-tidy not installed. Skipping."
    TOOLS_MISSING+=("clang-tidy")
fi

echo ""

# --- 3. clazy ---

echo -e "${BOLD}[3/4] clazy${NC} — Qt-Specific Analysis"

CLAZY_CMD=""
if command -v clazy-standalone &>/dev/null; then
    CLAZY_CMD="clazy-standalone"
elif command -v clazy &>/dev/null; then
    CLAZY_CMD="clazy"
fi

if [ -n "$CLAZY_CMD" ]; then
    if [ -n "$COMPILE_COMMANDS" ]; then
        CLAZY_OUTPUT=""
        for f in "${FILES[@]}"; do
            result=$($CLAZY_CMD -p "$COMPILE_DB_DIR" "$f" 2>&1) || true
            warnings=$(echo "$result" | grep -cE "warning:" 2>/dev/null) || warnings=0
            if [ "$warnings" -gt 0 ]; then
                CLAZY_OUTPUT+="$result"$'\n'
                CLAZY_ISSUES=$((CLAZY_ISSUES + warnings))
            fi
        done

        if [ $CLAZY_ISSUES -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} No Qt-specific issues found."
        else
            echo -e "  ${RED}✗${NC} $CLAZY_ISSUES Qt-specific warning(s) found:"
            echo "$CLAZY_OUTPUT" | grep -E "warning:" | head -30
            TOTAL_ISSUES=$((TOTAL_ISSUES + CLAZY_ISSUES))
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Skipping — clazy requires compile_commands.json for accurate results."
        echo -e "    See project config section above for how to generate it."
    fi
else
    echo -e "  ${YELLOW}⚠${NC} clazy not installed. Skipping."
    TOOLS_MISSING+=("clazy")
fi

echo ""

# --- 4. cppcheck ---

echo -e "${BOLD}[4/4] cppcheck${NC} — Supplementary Bug Finder"

if command -v cppcheck &>/dev/null; then
    CPPCHECK_ARGS=("--enable=warning,style,performance,portability" "--quiet" "--force")

    if [ -n "$COMPILE_COMMANDS" ]; then
        CPPCHECK_ARGS+=("--project=$COMPILE_COMMANDS")
        # When using --project, cppcheck picks files from compile_commands
        # Filter to only our changed files
        CPPCHECK_ARGS+=("--file-filter=$(IFS=,; echo "${FILES[*]}")")
        result=$(cppcheck "${CPPCHECK_ARGS[@]}" 2>&1) || true
    else
        result=$(cppcheck "${CPPCHECK_ARGS[@]}" "${FILES[@]}" 2>&1) || true
    fi

    CPPCHECK_ISSUES=$(echo "$result" | grep -cE "\[(warning|style|performance|portability|error)\]" 2>/dev/null) || CPPCHECK_ISSUES=0

    if [ $CPPCHECK_ISSUES -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} No issues found."
    else
        echo -e "  ${RED}✗${NC} $CPPCHECK_ISSUES issue(s) found:"
        echo "$result" | grep -E "\[(warning|style|performance|portability|error)\]" | head -30
        TOTAL_ISSUES=$((TOTAL_ISSUES + CPPCHECK_ISSUES))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} cppcheck not installed. Skipping."
    TOOLS_MISSING+=("cppcheck")
fi

echo ""

# --- Summary ---

echo "════════════════════════════════════════"
echo -e "${BOLD}Summary${NC}"
echo "────────────────────────────────────────"
echo -e "  clang-format:  ${FORMAT_ISSUES} file(s) need formatting"
echo -e "  clang-tidy:    ${TIDY_ISSUES} warning(s)"
echo -e "  clazy:         ${CLAZY_ISSUES} Qt-specific warning(s)"
echo -e "  cppcheck:      ${CPPCHECK_ISSUES} issue(s)"
echo -e "  ${BOLD}Total:         ${TOTAL_ISSUES} issue(s)${NC}"

if [ ${#TOOLS_MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing tools:${NC} ${TOOLS_MISSING[*]}"
    echo -e "Install with:"
    echo -e "  macOS:  brew install ${TOOLS_MISSING[*]}"
    echo -e "  Debian: sudo apt install ${TOOLS_MISSING[*]}"
fi

echo "════════════════════════════════════════"

if [ $TOTAL_ISSUES -gt 0 ]; then
    exit 1
else
    echo -e "${GREEN}All checks passed.${NC}"
    exit 0
fi
