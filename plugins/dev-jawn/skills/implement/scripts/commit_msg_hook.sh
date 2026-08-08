#!/bin/bash
# ABOUTME: Commit-msg hook that validates commit message format
# ABOUTME: Enforces type prefixes, issue references, and length limits

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Extract the first line (subject)
SUBJECT=$(echo "$COMMIT_MSG" | head -n 1)

# Skip merge commits
if [[ "$SUBJECT" =~ ^Merge ]]; then
    exit 0
fi

# Valid commit types
VALID_TYPES="Fix|Add|Update|Refactor|Remove|Docs|Test|Chore"

# Check 1: Subject line length (max 72 chars)
if [ ${#SUBJECT} -gt 72 ]; then
    echo "❌ ERROR: Commit subject exceeds 72 characters (${#SUBJECT} chars)"
    echo ""
    echo "Subject: $SUBJECT"
    echo ""
    echo "Please shorten your commit message subject line."
    exit 1
fi

# Check 2: Must start with valid type prefix (followed by space or colon)
if ! [[ "$SUBJECT" =~ ^($VALID_TYPES)([[:space:]]|:) ]]; then
    echo "❌ ERROR: Commit must start with a valid type prefix"
    echo ""
    echo "Your message: $SUBJECT"
    echo ""
    echo "Valid formats:"
    echo "  Fix #123: Description of the fix"
    echo "  Add #456: Description of new feature"
    echo "  Chore: Maintenance task description"
    echo ""
    echo "Valid types: Fix, Add, Update, Refactor, Remove, Docs, Test, Chore"
    exit 1
fi

# Check 3: Must have issue reference (except for Chore commits)
if [[ "$SUBJECT" =~ ^Chore ]]; then
    # Chore commits don't require issue numbers, but must have colon
    if ! [[ "$SUBJECT" =~ ^Chore:[[:space:]] ]]; then
        echo "❌ ERROR: Chore commits must follow format 'Chore: Description'"
        echo ""
        echo "Your message: $SUBJECT"
        exit 1
    fi
else
    # All other types require issue reference
    if ! [[ "$SUBJECT" =~ ^($VALID_TYPES)[[:space:]]#[0-9]+: ]]; then
        echo "❌ ERROR: Commit must reference an issue number"
        echo ""
        echo "Your message: $SUBJECT"
        echo ""
        echo "Required format: Type #123: Description"
        echo "Example: Fix #226: Resolve Spotlight indexing issue"
        echo ""
        echo "No issue? Create one first, or use 'Chore: Description' for maintenance tasks."
        exit 1
    fi
fi

echo "✅ Commit message format valid"
exit 0
