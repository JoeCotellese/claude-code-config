# Git Repository Benchmarks & Best Practices

## Commit Quality Benchmarks

### Commit Size

| Metric | Good | Acceptable | Concern |
|--------|------|------------|---------|
| Files per commit | 1-5 | 6-10 | >10 |
| Lines changed | <200 | 200-500 | >500 |
| Large commits (>10 files) | <5% | 5-15% | >15% |

**Why it matters:** Small, focused commits are easier to review, revert, and understand. Large commits often indicate rushed work or lack of incremental development discipline.

### Commit Message Quality

| Metric | Good | Acceptable | Concern |
|--------|------|------------|---------|
| Conventional commits % | >80% | 50-80% | <50% |
| Short messages (<10 chars) | <1% | 1-5% | >5% |
| WIP/temp commits | 0 | 1-5 | >5 |
| Message length | 50-72 chars | 30-100 chars | <30 or >100 |

**Conventional commit prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting (no code change)
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks
- `build:` - Build system changes
- `ci:` - CI configuration
- `perf:` - Performance improvement

## Branching Strategy Indicators

### Merge vs Rebase

| Pattern | Merge % | Typical Workflow |
|---------|---------|------------------|
| Rebase-heavy | <10% | Feature branches rebased, squash merges |
| Balanced | 10-40% | Mix of merge commits and rebases |
| Merge-heavy | >40% | Direct merges, merge commits preserved |

Neither is inherently better - consistency matters more than specific approach.

### Branch Hygiene

| Metric | Good | Acceptable | Concern |
|--------|------|------------|---------|
| Stale branches (>30d) | <5 | 5-15 | >15 |
| Average branch lifespan | <7 days | 7-14 days | >14 days |
| Branches without recent activity | <10% | 10-25% | >25% |

## Team Velocity Benchmarks

### Activity Distribution

| Metric | Healthy | Warning Sign |
|--------|---------|--------------|
| Weekend commits | <10% | >25% (burnout risk) |
| After-hours commits | <20% | >40% (work-life balance) |
| Commit-free days/week | 0-1 | >3 (sporadic development) |

### Contributor Health (Bus Factor)

| Top Contributor % | Risk Level | Recommendation |
|-------------------|------------|----------------|
| <30% | Low | Healthy distribution |
| 30-50% | Moderate | Encourage pair programming |
| 50-70% | High | Knowledge transfer needed |
| >70% | Critical | Urgent cross-training required |

### Active Contributors

| Team Size | Expected Active (30d) | Concern Level |
|-----------|----------------------|---------------|
| Small (2-5) | 80%+ | <50% |
| Medium (6-15) | 60%+ | <40% |
| Large (15+) | 40%+ | <25% |

## Code Churn Indicators

### Hotspot Analysis

Files appearing in top 10 most-changed list consistently may indicate:
- **Core business logic** - Expected for key files
- **Unstable design** - Frequent changes suggest unclear requirements
- **Bug-prone areas** - High correlation with fix commits

### Coupling Detection

Files frequently changed together suggest:
- **Intentional coupling** - Components designed to work together
- **Problematic coupling** - Changes in one always require changes in another
- **Missing abstraction** - Logic spread across multiple files

## Release Cadence Benchmarks

| Pattern | Tag Frequency | Characteristics |
|---------|---------------|-----------------|
| Continuous | Daily-Weekly | CI/CD, feature flags |
| Agile | Bi-weekly | Sprint-based releases |
| Traditional | Monthly+ | Longer release cycles |

### Healthy Release Patterns

- **Consistent intervals** - Predictable release rhythm
- **Semantic versioning** - Clear version progression
- **Reasonable commit count** - Not too few (wasted releases) or too many (risky releases)

## Repository Size Benchmarks

### Git Object Limits (via git-sizer)

| Metric | Acceptable | Warning | Critical |
|--------|------------|---------|----------|
| Total commits | <500k | 500k-1M | >1M |
| Max file size | <50MB | 50-100MB | >100MB |
| Max commit size | <50MB | 50-100MB | >100MB |
| Tree entries | <50k | 50-100k | >100k |

### Common Size Issues

- **Large binary files** - Use Git LFS
- **Vendor/node_modules committed** - Use .gitignore
- **Build artifacts** - Should be in .gitignore
- **Secrets/credentials** - Security risk, use git-crypt or remove

## Red Flags Checklist

### Immediate Concerns
- [ ] Secrets in commit history
- [ ] >1MB files in repository
- [ ] WIP commits on main branch
- [ ] Force pushes to main/master
- [ ] Single contributor >80% of code

### Process Concerns
- [ ] No conventional commit format
- [ ] Inconsistent branching strategy
- [ ] Many stale branches (>20)
- [ ] Irregular release cadence
- [ ] Large commits (>500 lines) frequent

### Team Health Concerns
- [ ] >50% weekend commits
- [ ] Single contributor dominance
- [ ] Long periods without commits
- [ ] High file churn without fixes

## Recommendations by Issue

### High Bus Factor
1. Implement pair programming rotation
2. Require code reviews from multiple team members
3. Document architectural decisions (ADRs)
4. Cross-train on critical system areas

### Poor Commit Quality
1. Adopt conventional commits standard
2. Set up commit message linting (commitlint)
3. Use pre-commit hooks for validation
4. Training on atomic commits

### Stale Branches
1. Implement branch cleanup automation
2. Set branch expiration policies
3. Regular branch audit in team meetings
4. Delete merged branches automatically

### Large Commits
1. Break work into smaller PRs
2. Use feature flags for incremental delivery
3. Implement trunk-based development
4. Review commit size in PR process
