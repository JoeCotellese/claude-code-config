#!/bin/bash
# ABOUTME: Detects project domain to select the correct code reviewer
# ABOUTME: Returns "swift", "python", "cpp-qt", or "unknown"
#
# Detection precedence (first match wins):
#   1. Swift/SwiftUI
#   2. Python
#   3. C++/Qt (least common, checked last)
#
# Usage:
#   DOMAIN=$(bash scripts/detect_project_domain.sh)
#   # or from repo root:
#   DOMAIN=$(bash skills/submit/scripts/detect_project_domain.sh /path/to/repo)

set -e

# Allow passing a directory argument, default to current directory
REPO_ROOT="${1:-.}"

# --- Swift / SwiftUI ---
# Package.swift (SPM), *.xcodeproj, *.xcworkspace, or project.pbxproj
if [ -f "$REPO_ROOT/Package.swift" ]; then
    echo "swift"
    exit 0
fi
if ls "$REPO_ROOT"/*.xcodeproj 1>/dev/null 2>&1 || \
   ls "$REPO_ROOT"/*.xcworkspace 1>/dev/null 2>&1; then
    echo "swift"
    exit 0
fi
# Check for .xcodeproj in immediate subdirectories (common monorepo layout)
if fd -t d -e xcodeproj --max-depth 2 --quiet . "$REPO_ROOT" 2>/dev/null; then
    echo "swift"
    exit 0
fi

# --- Python ---
# pyproject.toml, setup.py, setup.cfg, Pipfile, or requirements.txt
if [ -f "$REPO_ROOT/pyproject.toml" ] || \
   [ -f "$REPO_ROOT/setup.py" ] || \
   [ -f "$REPO_ROOT/setup.cfg" ] || \
   [ -f "$REPO_ROOT/Pipfile" ] || \
   [ -f "$REPO_ROOT/requirements.txt" ]; then
    echo "python"
    exit 0
fi

# --- C++ / Qt ---
# .pro files (qmake), CMakeLists.txt with Qt references, or conanfile with Qt
if ls "$REPO_ROOT"/*.pro 1>/dev/null 2>&1; then
    echo "cpp-qt"
    exit 0
fi
if [ -f "$REPO_ROOT/CMakeLists.txt" ]; then
    if grep -qi 'find_package.*Qt\|Qt[0-9]\|qt_add_' "$REPO_ROOT/CMakeLists.txt" 2>/dev/null; then
        echo "cpp-qt"
        exit 0
    fi
fi
if [ -f "$REPO_ROOT/conanfile.txt" ] || [ -f "$REPO_ROOT/conanfile.py" ]; then
    if grep -qi 'qt' "$REPO_ROOT/conanfile.txt" "$REPO_ROOT/conanfile.py" 2>/dev/null; then
        echo "cpp-qt"
        exit 0
    fi
fi

echo "unknown"
