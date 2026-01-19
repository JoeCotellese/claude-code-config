#!/usr/bin/env python3
# ABOUTME: Time-based reminder system for Claude Code hooks.
# ABOUTME: Injects priority interrupts for morning check-ins and afternoon task reviews.

import json
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "time-prompts-state.json"

# Configuration
DEBUG = False  # Set to True to always output (ignores time/state checks)
MORNING_START_HOUR = 7    # 7am
MORNING_END_HOUR = 9      # 9am
AFTERNOON_START_HOUR = 14 # 2pm
AFTERNOON_END_HOUR = 16   # 4pm


def load_state() -> dict:
    """Load the state file, or return empty state if it doesn't exist."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state: dict) -> None:
    """Save state to the state file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_today() -> str:
    """Get today's date as a string for state tracking."""
    return datetime.now().strftime("%Y-%m-%d")


def main():
    # Check for mode argument: "session_start" or "prompt_submit" (default)
    mode = sys.argv[1] if len(sys.argv) > 1 else "prompt_submit"

    now = datetime.now()
    current_hour = now.hour
    today = get_today()

    state = load_state()

    # Reset state if it's a new day
    if state.get("date") != today:
        state = {"date": today, "morning_shown": False, "afternoon_shown": False}

    output = None

    # Debug mode: always output
    if DEBUG:
        output = """
⏰ DEBUG TEST - HOOK OUTPUT CHECK

If you can see this message, the hook stdout IS being captured.
This is a test to verify the hook is working correctly.
"""
    elif mode == "session_start":
        # On session start: check if morning check-in happened today (regardless of time)
        if not state.get("morning_shown", False):
            state["morning_shown"] = True
            save_state(state)
            output = """
⏰ PRIORITY INTERRUPT - MORNING CHECK-IN

Before proceeding with the user's request, you MUST first ask:

"Good morning, Mr. C. Before we dive in — want to review your calendar and todo list for today?"

Use the managing-productivity skill or check their Todoist and calendar.
Do NOT proceed with their original request until they respond to this check-in.
"""
    else:
        # On prompt submit: use time windows
        # Check morning window (7am - 9am)
        if MORNING_START_HOUR <= current_hour < MORNING_END_HOUR and not state.get("morning_shown", False):
            state["morning_shown"] = True
            save_state(state)
            output = """
⏰ PRIORITY INTERRUPT - MORNING CHECK-IN

Before proceeding with the user's request, you MUST first ask:

"Good morning, Mr. C. Before we dive in — want to review your calendar and todo list for today?"

Use the managing-productivity skill or check their Todoist and calendar.
Do NOT proceed with their original request until they respond to this check-in.
"""

        # Check afternoon window (2pm - 4pm)
        elif AFTERNOON_START_HOUR <= current_hour < AFTERNOON_END_HOUR and not state.get("afternoon_shown", False):
            state["afternoon_shown"] = True
            save_state(state)
            output = """
⏰ PRIORITY INTERRUPT - AFTERNOON CHECK-IN

Before proceeding with the user's request, you MUST first ask:

"Afternoon check-in, Mr. C. Any new tasks or items that should go on your todo list?"

Help them capture any tasks that have come up during the day.
Do NOT proceed with their original request until they respond to this check-in.
"""

    # Log for debugging
    log_file = Path.home() / ".claude" / "time-reminders-debug.log"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} | mode={mode} | hour={current_hour} | state={state} | output={'YES' if output else 'NO'}\n")

    if output:
        print(output.strip(), flush=True)


if __name__ == "__main__":
    main()
