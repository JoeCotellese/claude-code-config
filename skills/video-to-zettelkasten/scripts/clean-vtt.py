#!/usr/bin/env python3
"""Clean a YouTube .vtt subtitle file into plain text.

Strips VTT headers, timestamp cues, and inline timing tags; collapses the
duplicate consecutive lines that auto-generated captions emit; merges all
content into a single whitespace-normalized paragraph.

Writes the result to a sibling .txt file (same basename) and prints the
output path plus word count.

Usage:
    python3 clean-vtt.py /tmp/yt-zk-<id>.en.vtt
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def clean(vtt_text: str) -> str:
    out: list[str] = []
    seen_last = ""
    for line in vtt_text.splitlines():
        if (
            line.startswith("WEBVTT")
            or line.startswith("Kind:")
            or line.startswith("Language:")
            or "-->" in line
            or not line.strip()
        ):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != seen_last:
            out.append(line)
            seen_last = line
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: clean-vtt.py <path-to.vtt>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 1
    cleaned = clean(src.read_text())
    dst = src.with_suffix(".txt") if src.suffix != ".txt" else src.with_name(src.stem + "-clean.txt")
    dst.write_text(cleaned)
    print(f"wrote {dst} ({len(cleaned.split())} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
