---
name: git-analysis
effort: medium
description: This skill should be used when the user wants to analyze a git repository's health, team practices, and development patterns. Use this when users ask to "analyze this repo", want to understand team velocity, commit patterns, branching strategies, contributor distribution, or assess git best practices compliance. Also use for questions like "how healthy is this codebase" or "what are the development patterns here".
---

# Git Analysis

## Overview

This skill provides comprehensive git repository analysis covering team practices, commit patterns, velocity metrics, and codebase health. It leverages both native git commands and open source analysis tools to generate actionable insights.

## Quick Start

To perform a comprehensive repository analysis:

1. Run `scripts/check_tools.sh` to verify available analysis tools
2. Run `scripts/analyze_repo.sh` for a full analysis report
3. For specific analyses, use the individual commands documented below

## Analysis Categories

### 1. Repository Overview

Quick snapshot of the repository:

```bash
# If onefetch is installed - visual repo summary
onefetch

# Native git alternative
git shortlog -sn --all | head -20  # Top contributors
git rev-list --count HEAD          # Total commits
git branch -a | wc -l              # Branch count
```

### 2. Commit Quality & Best Practices

**Commit Size Analysis:**
```bash
# Average files changed per commit (last 100 commits)
git log --oneline --shortstat -100 | grep "files\? changed" | awk '{sum+=$1; count++} END {print "Avg files/commit:", sum/count}'

# Large commits (>10 files changed) - potential code review issues
git log --oneline --shortstat | awk '/files? changed/ {if ($1 > 10) count++} END {print "Large commits (>10 files):", count}'

# Commits with very short messages (<10 chars) - quality indicator
git log --format="%s" | awk 'length($0) < 10 {count++} END {print "Short commit messages:", count}'
```

**Commit Message Quality:**
```bash
# Check for conventional commits format
git log --format="%s" -100 | grep -cE "^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\(.+\))?:"

# WIP/temp commits that should have been squashed
git log --oneline --all | grep -ciE "(wip|temp|fixup|squash|xxx|todo)"
```

**Co-authored commits (collaboration indicator):**
```bash
git log --all --oneline --grep="Co-authored-by" -i | wc -l
```

### 3. Branching Strategy Analysis

```bash
# Active branches
git branch -a --sort=-committerdate | head -20

# Branch naming patterns
git branch -a | sed 's/.*\///' | cut -d'-' -f1 | sort | uniq -c | sort -rn

# Stale branches (no commits in 30+ days)
git for-each-ref --sort=committerdate --format='%(refname:short) %(committerdate:relative)' refs/heads | while read branch date; do
  if [[ "$date" == *"months"* ]] || [[ "$date" == *"year"* ]]; then
    echo "STALE: $branch ($date)"
  fi
done

# Merge vs rebase detection (merge commits ratio)
total=$(git rev-list --count HEAD)
merges=$(git rev-list --merges --count HEAD)
echo "Merge commits: $merges / $total ($(( merges * 100 / total ))%)"
```

### 4. Team Velocity & Activity

```bash
# Commits per week (last 12 weeks)
git log --since="12 weeks ago" --format="%ai" | cut -d' ' -f1 | cut -d'-' -f1,2 | uniq -c

# Commits per author (last 30 days)
git shortlog -sn --since="30 days ago"

# Daily commit distribution
git log --format="%ad" --date=format:'%A' | sort | uniq -c | sort -rn

# Hourly commit distribution (work hours indicator)
git log --format="%ad" --date=format:'%H' | sort | uniq -c | sort -k2 -n
```

**Using git-quick-stats (if installed):**
```bash
git-quick-stats -T  # Commits by date
git-quick-stats -a  # Detailed stats by author
```

### 5. Contributor Analysis

```bash
# Bus factor - top contributors by percentage
git shortlog -sn --all | awk 'NR==1{total=$1} {sum+=$1; print $1, $1*100/total"%", $2}' | head -10

# Using git-fame (if installed) - more detailed analysis
git-fame --sort=commits --exclude="*.lock,*.json"

# New contributors (first commit in last 90 days)
git log --format="%an" --since="90 days ago" | sort -u | while read author; do
  first=$(git log --author="$author" --reverse --format="%ai" | head -1)
  if [[ "$first" > $(date -v-90d +%Y-%m-%d) ]]; then
    echo "NEW: $author (first commit: $first)"
  fi
done
```

### 6. Code Hotspots & Churn

```bash
# Most frequently changed files (last 6 months)
git log --since="6 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# Files changed together (coupling detection)
git log --name-only --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -30

# Bug fix frequency (files touched in "fix" commits)
git log --all --oneline --grep="fix" --name-only | grep -v "^[a-f0-9]" | sort | uniq -c | sort -rn | head -15
```

### 7. Release Cadence

```bash
# Tag history and frequency
git tag -l --sort=-creatordate | head -20

# Time between releases
git for-each-ref --sort=-creatordate --format='%(refname:short) %(creatordate:short)' refs/tags | head -10

# Commits since last tag
git describe --tags --abbrev=0 2>/dev/null && git rev-list $(git describe --tags --abbrev=0)..HEAD --count
```

### 8. Repository Size & Health

**Using git-sizer (if installed):**
```bash
git-sizer --verbose
```

**Native alternatives:**
```bash
# Repository size
du -sh .git

# Largest files in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print $3, $4}' | sort -rn | head -20

# File type distribution
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
```

## Open Source Tools Reference

| Tool | Install | Best For |
|------|---------|----------|
| onefetch | `brew install onefetch` | Quick visual repo summary |
| git-quick-stats | `brew install git-quick-stats` | Interactive stats menu |
| git-sizer | `brew install git-sizer` | Repo size/commit metrics |
| git-fame | `pip install git-fame` | Contributor analysis |
| mergestat | `brew install mergestat/tap/mergestat` | SQL queries on git |

To check which tools are available, run:
```bash
scripts/check_tools.sh
```

## Interpreting Results

See `references/benchmarks.md` for:
- Industry benchmarks for healthy repositories
- Red flags and warning signs
- Recommendations for common issues

## Resources

### scripts/

- `check_tools.sh` - Detect installed analysis tools and suggest missing ones
- `analyze_repo.sh` - Run comprehensive analysis and generate report

### references/

- `benchmarks.md` - Metric benchmarks, best practices thresholds, and interpretation guide
