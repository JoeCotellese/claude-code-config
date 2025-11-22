#!/usr/bin/env python3
# ABOUTME: Runs ruff and black checks on Python files and reports findings
# ABOUTME: Returns structured output with issues found for code review

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


def run_ruff(paths: List[str]) -> Dict[str, Any]:
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
            "error": "ruff not found. Install with: pip install ruff",
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


def run_black(paths: List[str], check_only: bool = True) -> Dict[str, Any]:
    """Run black formatter on specified paths.

    Args:
        paths: List of file or directory paths to check
        check_only: If True, only check formatting without modifying files

    Returns:
        Dict with 'success' bool and 'files_to_format' list
    """
    try:
        cmd = ["black", "--check", "--diff"] if check_only else ["black"]
        cmd.extend(paths)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return {"success": True, "files_to_format": []}

        # Parse output for files that would be reformatted
        files_to_format = []
        for line in result.stderr.split("\n"):
            if "would reformat" in line:
                # Extract filename from "would reformat /path/to/file.py"
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
            "error": "black not found. Install with: pip install black",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error running black: {e}",
        }


def format_output(ruff_result: Dict[str, Any], black_result: Dict[str, Any]) -> str:
    """Format results as human-readable text.

    Args:
        ruff_result: Result from run_ruff()
        black_result: Result from run_black()

    Returns:
        Formatted string with all findings
    """
    output = []

    # Ruff results
    output.append("=" * 80)
    output.append("RUFF LINTER RESULTS")
    output.append("=" * 80)

    if "error" in ruff_result:
        output.append(f"ERROR: {ruff_result['error']}")
    elif ruff_result["success"]:
        output.append("✓ No issues found")
    else:
        output.append(f"✗ Found {ruff_result['total_count']} issues\n")

        for file_path, issues in ruff_result["issues"].items():
            output.append(f"\n{file_path}:")
            for issue in issues:
                location = f"{issue['line']}:{issue['column']}"
                severity = issue['severity'].upper()
                output.append(
                    f"  {location:10} [{severity}] {issue['code']}: {issue['message']}"
                )

    # Black results
    output.append("\n")
    output.append("=" * 80)
    output.append("BLACK FORMATTER RESULTS")
    output.append("=" * 80)

    if "error" in black_result:
        output.append(f"ERROR: {black_result['error']}")
    elif black_result["success"]:
        output.append("✓ All files properly formatted")
    else:
        output.append(f"✗ {len(black_result['files_to_format'])} files need formatting:\n")
        for file_path in black_result["files_to_format"]:
            output.append(f"  - {file_path}")

        if black_result.get("diff"):
            output.append("\nFormatting diff:")
            output.append(black_result["diff"])

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

    print("Running ruff and black checks...\n")

    ruff_result = run_ruff(paths)
    black_result = run_black(paths)

    output = format_output(ruff_result, black_result)
    print(output)

    # Exit with non-zero if any issues found
    has_issues = (
        not ruff_result.get("success", False) or
        not black_result.get("success", False)
    )
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
