#!/bin/bash
# ABOUTME: Detects the primary technology/domain of a project
# ABOUTME: Returns: swift, react-native, python, or unknown

# Check for Swift/iOS project
if ls *.xcodeproj >/dev/null 2>&1 || ls *.xcworkspace >/dev/null 2>&1; then
    echo "swift"
    exit 0
fi

# Check for React Native
if [ -f "package.json" ] && grep -q "react-native" package.json 2>/dev/null; then
    echo "react-native"
    exit 0
fi

# Check for Python
if ls *.py >/dev/null 2>&1 || [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    echo "python"
    exit 0
fi

# Check for generic Node.js/TypeScript
if [ -f "package.json" ]; then
    echo "typescript"
    exit 0
fi

echo "unknown"
