#!/usr/bin/env python3
"""Send text content to Drafts app via URL scheme."""
import subprocess
import sys
import urllib.parse

text = sys.stdin.read()
encoded = urllib.parse.quote(text)
url = f"drafts://x-callback-url/create?text={encoded}"
subprocess.run(["open", url])
