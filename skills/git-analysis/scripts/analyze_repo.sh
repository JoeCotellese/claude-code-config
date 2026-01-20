#!/bin/bash
# ABOUTME: Runs comprehensive git repository analysis and outputs a structured report.
# ABOUTME: Uses native git commands with optional enhancement from installed tools.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

subheader() {
    echo ""
    echo -e "${YELLOW}▸ $1${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}Error: Not a git repository${NC}"
    exit 1
fi

REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
ANALYSIS_DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           GIT REPOSITORY ANALYSIS REPORT                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Repository: $REPO_NAME"
echo "Analysis Date: $ANALYSIS_DATE"

# ============================================
header "1. REPOSITORY OVERVIEW"
# ============================================

if command -v onefetch &> /dev/null; then
    onefetch 2>/dev/null || true
else
    subheader "Basic Stats"
    echo "Total commits: $(git rev-list --count HEAD 2>/dev/null || echo 'N/A')"
    echo "Total branches: $(git branch -a 2>/dev/null | wc -l | tr -d ' ')"
    echo "Total tags: $(git tag -l 2>/dev/null | wc -l | tr -d ' ')"
    echo "Repository size: $(du -sh .git 2>/dev/null | cut -f1)"

    subheader "Language Distribution (by file count)"
    git ls-files 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10
fi

# ============================================
header "2. COMMIT QUALITY ANALYSIS"
# ============================================

subheader "Commit Size Metrics"
avg_files=$(git log --oneline --shortstat -100 2>/dev/null | grep "files\? changed" | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "N/A"}')
echo "Average files per commit (last 100): $avg_files"

large_commits=$(git log --oneline --shortstat 2>/dev/null | awk '/files? changed/ {if ($1 > 10) count++} END {print count+0}')
echo "Large commits (>10 files): $large_commits"

subheader "Commit Message Quality"
total_commits=$(git rev-list --count HEAD 2>/dev/null || echo 0)
conventional=$(git log --format="%s" -100 2>/dev/null | grep -cE "^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\(.+\))?:" || echo 0)
echo "Conventional commits (last 100): $conventional/100"

short_msgs=$(git log --format="%s" 2>/dev/null | awk 'length($0) < 10 {count++} END {print count+0}')
echo "Short commit messages (<10 chars): $short_msgs"

wip_commits=$(git log --oneline --all 2>/dev/null | grep -ciE "(wip|temp|fixup|squash|xxx)" || echo 0)
echo "WIP/temp commits (should be squashed): $wip_commits"

subheader "Collaboration Indicators"
coauthored=$(git log --all --oneline --grep="Co-authored-by" -i 2>/dev/null | wc -l | tr -d ' ')
echo "Co-authored commits: $coauthored"

# ============================================
header "3. BRANCHING STRATEGY"
# ============================================

subheader "Active Branches (most recent first)"
git branch -a --sort=-committerdate 2>/dev/null | head -10

subheader "Branch Naming Patterns"
git branch -a 2>/dev/null | sed 's/.*\///' | cut -d'-' -f1 | sort | uniq -c | sort -rn | head -5

subheader "Merge vs Rebase Analysis"
total=$(git rev-list --count HEAD 2>/dev/null || echo 1)
merges=$(git rev-list --merges --count HEAD 2>/dev/null || echo 0)
if [ "$total" -gt 0 ]; then
    pct=$((merges * 100 / total))
    echo "Merge commits: $merges / $total ($pct%)"
    if [ "$pct" -gt 50 ]; then
        echo -e "${YELLOW}  ⚠ High merge commit ratio suggests merge-based workflow${NC}"
    elif [ "$pct" -lt 10 ]; then
        echo -e "${GREEN}  ✓ Low merge ratio suggests rebase-based workflow${NC}"
    fi
fi

# ============================================
header "4. TEAM VELOCITY & ACTIVITY"
# ============================================

subheader "Commits Per Author (Last 30 Days)"
git shortlog -sn --since="30 days ago" 2>/dev/null | head -10

subheader "Daily Commit Distribution"
git log --format="%ad" --date=format:'%A' 2>/dev/null | sort | uniq -c | sort -rn

subheader "Hourly Distribution (Work Hours Analysis)"
echo "Hour  Count"
git log --format="%ad" --date=format:'%H' 2>/dev/null | sort | uniq -c | sort -k2 -n | awk '{printf "%s:00  %s\n", $2, $1}'

# ============================================
header "5. CONTRIBUTOR ANALYSIS"
# ============================================

subheader "Top Contributors (All Time)"
git shortlog -sn --all 2>/dev/null | head -10

subheader "Bus Factor Analysis"
top_contributor_pct=$(git shortlog -sn --all 2>/dev/null | head -1 | awk -v total="$total_commits" '{if(total>0) printf "%.0f", $1*100/total; else print "N/A"}')
echo "Top contributor owns: ${top_contributor_pct}% of commits"
if [ "$top_contributor_pct" != "N/A" ] && [ "$top_contributor_pct" -gt 80 ]; then
    echo -e "${RED}  ⚠ HIGH RISK: Single contributor dominance${NC}"
elif [ "$top_contributor_pct" != "N/A" ] && [ "$top_contributor_pct" -gt 50 ]; then
    echo -e "${YELLOW}  ⚠ MODERATE RISK: Consider knowledge sharing${NC}"
else
    echo -e "${GREEN}  ✓ Healthy distribution of contributions${NC}"
fi

if command -v git-fame &> /dev/null; then
    subheader "Detailed Contributor Stats (git-fame)"
    git-fame --sort=commits --exclude="*.lock,*.json,package-lock.json,yarn.lock" 2>/dev/null | head -15 || true
fi

# ============================================
header "6. CODE HOTSPOTS"
# ============================================

subheader "Most Frequently Changed Files (Last 6 Months)"
git log --since="6 months ago" --name-only --pretty=format: 2>/dev/null | grep -v '^$' | sort | uniq -c | sort -rn | head -15

subheader "Bug Fix Hotspots (Files in 'fix' commits)"
git log --all --oneline --grep="fix" -i --name-only 2>/dev/null | grep -v "^[a-f0-9]" | grep -v '^$' | sort | uniq -c | sort -rn | head -10

# ============================================
header "7. RELEASE CADENCE"
# ============================================

subheader "Recent Tags"
git for-each-ref --sort=-creatordate --format='%(refname:short) %(creatordate:short)' refs/tags 2>/dev/null | head -10

last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$last_tag" ]; then
    commits_since=$(git rev-list "$last_tag"..HEAD --count 2>/dev/null || echo "N/A")
    echo ""
    echo "Commits since last tag ($last_tag): $commits_since"
fi

# ============================================
header "8. REPOSITORY HEALTH"
# ============================================

if command -v git-sizer &> /dev/null; then
    subheader "Size Analysis (git-sizer)"
    git-sizer 2>/dev/null || true
else
    subheader "Size Metrics"
    echo "Repository size: $(du -sh .git 2>/dev/null | cut -f1)"
    echo "Working tree files: $(git ls-files 2>/dev/null | wc -l | tr -d ' ')"
fi

subheader "File Type Distribution"
git ls-files 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10

# ============================================
header "SUMMARY"
# ============================================

echo ""
echo "📊 Key Metrics:"
echo "   • Total commits: $total_commits"
echo "   • Active contributors (30d): $(git shortlog -sn --since='30 days ago' 2>/dev/null | wc -l | tr -d ' ')"
echo "   • Conventional commits: $conventional%"
echo "   • Merge commit ratio: ${pct:-N/A}%"
echo "   • Top contributor share: ${top_contributor_pct}%"
echo ""
echo "Analysis complete. See references/benchmarks.md for interpretation guidance."
echo ""
