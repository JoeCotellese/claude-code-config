#!/bin/bash
# ABOUTME: Detects project domain to select the correct code reviewer
# ABOUTME: Returns "swift", "python", "cpp-qt", "ambiguous:<a>,<b>", or "unknown"
#
# Every domain is checked. A repo matching more than one reports the collision
# rather than resolving it silently by precedence, because a Swift+Python
# monorepo needs a human to say which reviewer the diff wants.
#
# Output contract:
#   swift | python | cpp-qt   exactly one domain matched
#   ambiguous:swift,python    more than one matched; /submit STOPs and asks
#   unknown                   none matched; /submit acknowledges and continues
#
# Usage:
#   DOMAIN=$(bash scripts/detect_project_domain.sh)
#   # or from repo root:
#   DOMAIN=$(bash skills/submit/scripts/detect_project_domain.sh /path/to/repo)

set -u

# Allow passing a directory argument, default to current directory
REPO_ROOT="${1:-.}"

# --- Swift / SwiftUI ---
# Package.swift (SPM), *.xcodeproj, *.xcworkspace, including the common
# monorepo layout that keeps the project one level down.
is_swift() {
    [ -f "$REPO_ROOT/Package.swift" ] && return 0
    ls "$REPO_ROOT"/*.xcodeproj 1>/dev/null 2>&1 && return 0
    ls "$REPO_ROOT"/*.xcworkspace 1>/dev/null 2>&1 && return 0
    fd -t d -e xcodeproj --max-depth 2 --quiet . "$REPO_ROOT" 2>/dev/null && return 0
    return 1
}

# --- Python ---
is_python() {
    [ -f "$REPO_ROOT/pyproject.toml" ] && return 0
    [ -f "$REPO_ROOT/setup.py" ] && return 0
    [ -f "$REPO_ROOT/setup.cfg" ] && return 0
    [ -f "$REPO_ROOT/Pipfile" ] && return 0
    [ -f "$REPO_ROOT/requirements.txt" ] && return 0
    return 1
}

# --- C++ / Qt ---
# .pro files (qmake), CMakeLists.txt with Qt references, or conanfile with Qt.
# CMake and conan alone are not enough: both are used far outside Qt.
is_cpp_qt() {
    ls "$REPO_ROOT"/*.pro 1>/dev/null 2>&1 && return 0
    if [ -f "$REPO_ROOT/CMakeLists.txt" ]; then
        grep -qi 'find_package.*Qt\|Qt[0-9]\|qt_add_' "$REPO_ROOT/CMakeLists.txt" 2>/dev/null && return 0
    fi
    if [ -f "$REPO_ROOT/conanfile.txt" ] || [ -f "$REPO_ROOT/conanfile.py" ]; then
        grep -qi 'qt' "$REPO_ROOT/conanfile.txt" "$REPO_ROOT/conanfile.py" 2>/dev/null && return 0
    fi
    return 1
}

matches=""
is_swift   && matches="$matches swift"
is_python  && matches="$matches python"
is_cpp_qt  && matches="$matches cpp-qt"

# shellcheck disable=SC2086
set -- $matches

case $# in
    0) echo "unknown" ;;
    1) echo "$1" ;;
    *) echo "ambiguous:$(echo "$matches" | tr -s ' ' | sed 's/^ //; s/ /,/g')" ;;
esac
