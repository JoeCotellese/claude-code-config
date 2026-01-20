#!/bin/bash
# ABOUTME: Checks for installed git analysis tools and suggests installation commands
# ABOUTME: for any missing tools. Run before analysis to understand available capabilities.

set -euo pipefail

echo "🔍 Git Analysis Tools Check"
echo "============================"
echo ""

check_tool() {
    local tool=$1
    local install_cmd=$2
    local description=$3

    if command -v "$tool" &> /dev/null; then
        version=$($tool --version 2>/dev/null | head -1 || echo "installed")
        echo "✅ $tool - $description"
        echo "   Version: $version"
    else
        echo "❌ $tool - $description"
        echo "   Install: $install_cmd"
    fi
    echo ""
}

echo "=== Core Analysis Tools ==="
echo ""

check_tool "onefetch" \
    "brew install onefetch" \
    "Visual repo summary with language stats"

check_tool "git-quick-stats" \
    "brew install git-quick-stats" \
    "Interactive git statistics menu"

check_tool "git-sizer" \
    "brew install git-sizer" \
    "Repository size metrics and warnings"

check_tool "git-fame" \
    "pip install git-fame" \
    "Detailed contributor analysis"

check_tool "mergestat" \
    "brew install mergestat/tap/mergestat" \
    "SQL queries on git repositories"

echo "=== Optional Enhancement Tools ==="
echo ""

check_tool "gitleaks" \
    "brew install gitleaks" \
    "Secret/credential scanning"

check_tool "gitinspector" \
    "pip install gitinspector" \
    "Statistical analysis with blame"

echo "============================"
echo ""
echo "💡 Tip: Install all recommended tools with:"
echo "   brew install onefetch git-quick-stats git-sizer mergestat/tap/mergestat"
echo "   pip install git-fame"
echo ""
