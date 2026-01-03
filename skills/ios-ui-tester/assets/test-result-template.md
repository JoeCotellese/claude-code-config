# Test Run: {Test Name from YAML}

- **Date:** YYYY-MM-DD HH:MM
- **Status:** PASS | FAIL | PASS (with caveats)
- **YAML:** {yaml_filename.yaml}
- **Simulator:** {UDID} ({Device Name})

## Precondition

- **Expected:** {What screen/state the test expects to start from}
- **Actual:** {What screen/state was actually present}
- **Recovery:** {Steps taken to reach expected state, or "None needed"}

## Steps

| Step | Action | Expected | Actual | Status |
|------|--------|----------|--------|--------|
| 1 | {Action taken} | {Expected result} | {Actual result} | PASS/FAIL |
| 2 | {Action taken} | {Expected result} | {Actual result} | PASS/FAIL |

## Issues Encountered

{List any issues, with resolution if applicable. Use "None" if no issues.}

1. **{Issue title}**
   - {Description of what happened}
   - **Resolution:** {How it was resolved}

## Notes

- {Useful observations for future test runs}
- {Coordinates, element IDs, or patterns discovered}
- {Any flaky behavior or timing-sensitive steps}

## Final State

{Description of app state after test completion}
