#!/usr/bin/env python3
# ABOUTME: Runs ruff linter and ruff formatter checks on Python files and reports findings
# ABOUTME: Returns structured output with issues found for code review

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


def run_ruff_lint(paths: List[str]) -> Dict[str, Any]:
    """Run ruff linter on specified paths.

    Args:
        paths: List of file or directory paths to check

    Returns:
        Dict with 'success' bool and 'issues' list
    """
    try:
        result = subprocess.run(
            ["ruff", "check", "--output-format=json", *paths],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return {"success": True, "issues": []}

        # Parse JSON output
        issues = json.loads(result.stdout) if result.stdout else []

        # Group issues by file
        by_file = {}
        for issue in issues:
            file_path = issue.get("filename", "unknown")
            if file_path not in by_file:
                by_file[file_path] = []

            by_file[file_path].append({
                "line": issue.get("location", {}).get("row"),
                "column": issue.get("location", {}).get("column"),
                "code": issue.get("code"),
                "message": issue.get("message"),
                "severity": "error" if issue.get("code", "").startswith("E") else "warning",
            })

        return {
            "success": False,
            "issues": by_file,
            "total_count": len(issues),
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "ruff not found. Install with: uv tool install ruff",
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse ruff output: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error running ruff: {e}",
        }


def run_ruff_format(paths: List[str]) -> Dict[str, Any]:
    """Run ruff formatter check on specified paths.

    Args:
        paths: List of file or directory paths to check

    Returns:
        Dict with 'success' bool and 'files_to_format' list
    """
    try:
        result = subprocess.run(
            ["ruff", "format", "--check", "--diff", *paths],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return {"success": True, "files_to_format": []}

        # Parse stderr for files that would be reformatted
        files_to_format = []
        for line in result.stderr.split("\n"):
            if "would reformat" in line.lower():
                parts = line.split()
                if len(parts) >= 3:
                    files_to_format.append(parts[2])

        return {
            "success": False,
            "files_to_format": files_to_format,
            "diff": result.stdout if result.stdout else None,
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "ruff not found. Install with: uv tool install ruff",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error running ruff format: {e}",
        }


def format_output(lint_result: Dict[str, Any], fmt_result: Dict[str, Any]) -> str:
    """Format results as human-readable text.

    Args:
        lint_result: Result from run_ruff_lint()
        fmt_result: Result from run_ruff_format()

    Returns:
        Formatted string with all findings
    """
    output = []

    # Lint results
    output.append("=" * 80)
    output.append("RUFF LINTER RESULTS")
    output.append("=" * 80)

    if "error" in lint_result:
        output.append(f"ERROR: {lint_result['error']}")
    elif lint_result["success"]:
        output.append("✓ No issues found")
    else:
        output.append(f"✗ Found {lint_result['total_count']} issues\n")

        for file_path, issues in lint_result["issues"].items():
            output.append(f"\n{file_path}:")
            for issue in issues:
                location = f"{issue['line']}:{issue['column']}"
                severity = issue['severity'].upper()
                output.append(
                    f"  {location:10} [{severity}] {issue['code']}: {issue['message']}"
                )

    # Format results
    output.append("\n")
    output.append("=" * 80)
    output.append("RUFF FORMATTER RESULTS")
    output.append("=" * 80)

    if "error" in fmt_result:
        output.append(f"ERROR: {fmt_result['error']}")
    elif fmt_result["success"]:
        output.append("✓ All files properly formatted")
    else:
        output.append(f"✗ {len(fmt_result['files_to_format'])} files need formatting:\n")
        for file_path in fmt_result["files_to_format"]:
            output.append(f"  - {file_path}")

        if fmt_result.get("diff"):
            output.append("\nFormatting diff:")
            output.append(fmt_result["diff"])

    return "\n".join(output)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: run_checks.py <path1> [path2 ...]", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  run_checks.py src/", file=sys.stderr)
        print("  run_checks.py file1.py file2.py", file=sys.stderr)
        print("  run_checks.py .", file=sys.stderr)
        sys.exit(1)

    paths = sys.argv[1:]

    # Validate paths exist
    for path in paths:
        if not Path(path).exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            sys.exit(1)

    print("Running ruff lint and format checks...\n")

    lint_result = run_ruff_lint(paths)
    fmt_result = run_ruff_format(paths)

    output = format_output(lint_result, fmt_result)
    print(output)

    # Exit with non-zero if any issues found
    has_issues = (
        not lint_result.get("success", False) or
        not fmt_result.get("success", False)
    )
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
