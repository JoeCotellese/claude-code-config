
# Git

- NEVER add Claude attribution to git commit messages

# GitLab Integration

- **ALWAYS use `glab` CLI for GitLab operations** instead of web interface or git commands
- Use `glab` for:
  - Creating and managing issues: `glab issue create`, `glab issue list`
  - Working with merge requests: `glab mr create`, `glab mr view`
  - Managing pipelines: `glab pipeline status`
  - Project operations: `glab project view`
- Never use GitHub CLI (`gh`) for GitLab projects - use `glab` exclusively

# Branch Naming Convention

**ALWAYS use namespaced branch names** with the following prefixes:

## Branch Prefixes

- `feature/N-description` - New features or enhancements
  - Example: `feature/44-meditation-trigger-tracking`
  - Use for: New functionality, new capabilities, user-facing additions

- `fix/N-description` or `bugfix/N-description` - Bug fixes
  - Example: `fix/23-timer-crash-on-pause`
  - Use for: Fixing broken functionality, addressing reported bugs

- `hotfix/N-description` - Urgent production fixes
  - Example: `hotfix/67-critical-data-loss`
  - Use for: Critical issues requiring immediate deployment

- `chore/N-description` - Maintenance, refactoring, tooling
  - Example: `chore/12-update-dependencies`
  - Use for: Dependency updates, code cleanup, build config, CI/CD changes

- `docs/N-description` - Documentation updates
  - Example: `docs/89-api-documentation`
  - Use for: README updates, code comments, user guides

- `test/N-description` - Test improvements
  - Example: `test/45-integration-test-coverage`
  - Use for: Adding tests, improving test infrastructure

- `refactor/N-description` - Code refactoring without functionality changes
  - Example: `refactor/34-extract-analytics-service`
  - Use for: Restructuring code, improving architecture, no behavior change

## Workflow

1. **Create issue** in GitLab first (or use existing issue number)
2. **Create branch** from main with proper namespace:
   ```bash
   git checkout -b feature/N-description
   ```
3. **Make changes and commit**
4. **Push branch**:
   ```bash
   git push -u origin feature/N-description
   ```
5. **Create MR** - ALWAYS specify source branch explicitly:
   ```bash
   glab mr create \
     --source-branch feature/N-description \
     --target-branch main \
     --title "Title" \
     --description "..." \
     --draft \
     --related-issue N
   ```

## Important Notes

- **NEVER omit `--source-branch`** in `glab mr create` - GitLab will auto-generate a branch name from the issue (e.g., `N-description` without prefix) which creates confusion
- **ALWAYS use the namespace prefix** - this prevents branch name conflicts and makes auto-generated branches obviously wrong
- **Match issue number** - Use `N` from issue #N in branch name for traceability
- **Keep descriptions short** - Use kebab-case, focus on the key change
- **Delete merged branches** - Clean up remote branches after MR is merged
