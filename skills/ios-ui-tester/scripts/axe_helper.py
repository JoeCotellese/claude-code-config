# ABOUTME: Generic Python wrapper for AXe iOS Simulator CLI - app agnostic
# ABOUTME: Provides element finding by accessibility ID, tapping, typing, gestures, and assertions

"""
AXe Helper - Generic iOS UI Testing Wrapper

This module provides a Python interface to the AXe CLI tool for iOS Simulator
automation. It enables finding elements by accessibility identifier and
performing interactions like tapping, typing, and gestures.

Usage:
    from axe_helper import AXeHelper

    axe = AXeHelper(udid="YOUR-SIMULATOR-UDID")
    axe.tap("loginButton")
    axe.type_text("hello@example.com")
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class Element:
    """Represents a UI element found via AXe describe-ui."""

    accessibility_id: str | None
    label: str | None
    element_type: str
    frame: dict[str, float]
    enabled: bool
    children: list[dict[str, Any]]
    raw: dict[str, Any]

    @property
    def center_x(self) -> int:
        """Calculate center X coordinate for tapping."""
        return int(self.frame["x"] + self.frame["width"] / 2)

    @property
    def center_y(self) -> int:
        """Calculate center Y coordinate for tapping."""
        return int(self.frame["y"] + self.frame["height"] / 2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Element:
        """Create Element from AXe describe-ui JSON."""
        return cls(
            accessibility_id=data.get("AXUniqueId"),
            label=data.get("AXLabel"),
            element_type=data.get("type", "Unknown"),
            frame=data.get("frame", {"x": 0, "y": 0, "width": 0, "height": 0}),
            enabled=data.get("enabled", False),
            children=data.get("children", []),
            raw=data,
        )


class AXeError(Exception):
    """Base exception for AXe operations."""

    pass


class ElementNotFoundError(AXeError):
    """Raised when an element cannot be found."""

    pass


class TimeoutError(AXeError):
    """Raised when waiting for an element times out."""

    pass


class AXeHelper:
    """
    Generic AXe wrapper for iOS UI testing.

    Provides methods to find elements by accessibility identifier,
    interact with the UI (tap, type, gesture), and make assertions.
    """

    def __init__(self, udid: str, app_bundle_id: str | None = None):
        """
        Initialize AXeHelper.

        Args:
            udid: Simulator UDID (required)
            app_bundle_id: Optional bundle ID for app-specific operations
        """
        self.udid = udid
        self.app_bundle_id = app_bundle_id

    def _run_axe(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run an AXe command and return the result."""
        cmd = ["axe", *args, "--udid", self.udid]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if check and result.returncode != 0:
            raise AXeError(f"AXe command failed: {' '.join(cmd)}\n{result.stderr}")
        return result

    # -------------------------------------------------------------------------
    # Core UI Inspection
    # -------------------------------------------------------------------------

    def get_ui_tree(self) -> list[dict[str, Any]]:
        """
        Get the current UI hierarchy as parsed JSON.

        Returns:
            List of element dictionaries from describe-ui
        """
        result = self._run_axe("describe-ui")
        # Filter out warning lines (start with "objc[" or similar)
        lines = result.stdout.strip().split("\n")
        json_lines = [line for line in lines if not line.startswith("objc[")]
        json_str = "\n".join(json_lines)
        return json.loads(json_str)

    def _find_in_tree(
        self,
        elements: list[dict[str, Any]],
        predicate: callable,
        find_all: bool = False,
    ) -> list[Element]:
        """Recursively search UI tree for elements matching predicate."""
        results = []
        for elem in elements:
            if predicate(elem):
                results.append(Element.from_dict(elem))
                if not find_all:
                    return results
            # Recurse into children
            children = elem.get("children", [])
            if children:
                child_results = self._find_in_tree(children, predicate, find_all)
                results.extend(child_results)
                if not find_all and results:
                    return results
        return results

    def find_element(self, accessibility_id: str) -> Element | None:
        """
        Find a single element by its accessibility identifier (AXUniqueId).

        Args:
            accessibility_id: The accessibility identifier to search for

        Returns:
            Element if found, None otherwise
        """
        tree = self.get_ui_tree()
        results = self._find_in_tree(
            tree, lambda e: e.get("AXUniqueId") == accessibility_id, find_all=False
        )
        return results[0] if results else None

    def find_elements(self, accessibility_id: str) -> list[Element]:
        """
        Find all elements matching an accessibility identifier.

        Args:
            accessibility_id: The accessibility identifier to search for

        Returns:
            List of matching Elements (may be empty)
        """
        tree = self.get_ui_tree()
        return self._find_in_tree(
            tree, lambda e: e.get("AXUniqueId") == accessibility_id, find_all=True
        )

    def find_by_label(self, label: str, partial: bool = False) -> Element | None:
        """
        Find element by its AXLabel text.

        Args:
            label: The label text to search for
            partial: If True, match partial label text

        Returns:
            Element if found, None otherwise
        """
        tree = self.get_ui_tree()
        if partial:
            predicate = lambda e: label in (e.get("AXLabel") or "")
        else:
            predicate = lambda e: e.get("AXLabel") == label
        results = self._find_in_tree(tree, predicate, find_all=False)
        return results[0] if results else None

    def find_by_type(self, element_type: str) -> list[Element]:
        """
        Find all elements of a specific type (Button, TextField, etc.).

        Args:
            element_type: The element type to search for

        Returns:
            List of matching Elements
        """
        tree = self.get_ui_tree()
        return self._find_in_tree(
            tree, lambda e: e.get("type") == element_type, find_all=True
        )

    # -------------------------------------------------------------------------
    # Interactions
    # -------------------------------------------------------------------------

    def tap_coordinates(self, x: int, y: int, post_delay: float = 0.0) -> None:
        """
        Tap at specific screen coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            post_delay: Optional delay after tap (seconds)
        """
        args = ["tap", "-x", str(x), "-y", str(y)]
        if post_delay > 0:
            args.extend(["--post-delay", str(post_delay)])
        self._run_axe(*args)

    def tap(
        self, accessibility_id: str, timeout: float = 5.0, post_delay: float = 0.5
    ) -> None:
        """
        Find element by accessibility ID and tap its center.

        Args:
            accessibility_id: The accessibility identifier to tap
            timeout: Max time to wait for element (seconds)
            post_delay: Delay after tap for UI to settle (seconds)

        Raises:
            ElementNotFoundError: If element not found within timeout
        """
        element = self.wait_for_element(accessibility_id, timeout=timeout)
        self.tap_coordinates(element.center_x, element.center_y, post_delay=post_delay)

    def tap_label(
        self, label: str, timeout: float = 5.0, post_delay: float = 0.5
    ) -> None:
        """
        Find element by label text and tap its center.

        Args:
            label: The label text to find and tap
            timeout: Max time to wait for element (seconds)
            post_delay: Delay after tap (seconds)

        Raises:
            ElementNotFoundError: If element not found within timeout
        """
        element = self.wait_for_label(label, timeout=timeout)
        self.tap_coordinates(element.center_x, element.center_y, post_delay=post_delay)

    def type_text(self, text: str) -> None:
        """
        Type text (element should already be focused).

        Uses stdin to avoid shell escaping issues with special characters.

        Args:
            text: Text to type
        """
        cmd = ["axe", "type", "--stdin", "--udid", self.udid]
        subprocess.run(cmd, input=text, text=True, check=True)

    def clear_and_type(
        self, accessibility_id: str, text: str, timeout: float = 5.0
    ) -> None:
        """
        Tap a text field, clear it, and type new text.

        Args:
            accessibility_id: The text field's accessibility identifier
            text: Text to enter
            timeout: Max time to wait for element (seconds)
        """
        self.tap(accessibility_id, timeout=timeout, post_delay=0.3)
        # Select all and delete (Cmd+A, then backspace)
        # For iOS text fields, triple-tap often selects all
        element = self.find_element(accessibility_id)
        if element:
            # Triple tap to select all
            for _ in range(3):
                self.tap_coordinates(element.center_x, element.center_y, post_delay=0.1)
            time.sleep(0.2)
            # Delete selected text
            self._run_axe("key", "42")  # Backspace
            time.sleep(0.1)
        self.type_text(text)

    # -------------------------------------------------------------------------
    # Gestures
    # -------------------------------------------------------------------------

    def scroll_down(self, duration: float = 0.5) -> None:
        """Scroll content downward (swipe up gesture)."""
        args = ["gesture", "scroll-down", "--duration", str(duration)]
        self._run_axe(*args)

    def scroll_up(self, duration: float = 0.5) -> None:
        """Scroll content upward (swipe down gesture)."""
        args = ["gesture", "scroll-up", "--duration", str(duration)]
        self._run_axe(*args)

    def swipe_back(self) -> None:
        """Swipe from left edge to navigate back."""
        self._run_axe("gesture", "swipe-from-left-edge")

    def swipe_dismiss(self) -> None:
        """Swipe down from top to dismiss."""
        self._run_axe("gesture", "swipe-from-top-edge")

    def pull_to_refresh(self) -> None:
        """Pull down to refresh (longer scroll-down gesture)."""
        self.scroll_down(duration=0.8)

    # -------------------------------------------------------------------------
    # Waiting & Assertions
    # -------------------------------------------------------------------------

    def wait_for_element(
        self, accessibility_id: str, timeout: float = 10.0, poll_interval: float = 0.5
    ) -> Element:
        """
        Poll until element appears or timeout.

        Args:
            accessibility_id: The accessibility identifier to wait for
            timeout: Maximum wait time (seconds)
            poll_interval: Time between checks (seconds)

        Returns:
            The found Element

        Raises:
            TimeoutError: If element not found within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            element = self.find_element(accessibility_id)
            if element:
                return element
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Element '{accessibility_id}' not found within {timeout}s"
        )

    def wait_for_label(
        self, label: str, timeout: float = 10.0, poll_interval: float = 0.5
    ) -> Element:
        """
        Poll until element with label appears or timeout.

        Args:
            label: The label text to wait for
            timeout: Maximum wait time (seconds)
            poll_interval: Time between checks (seconds)

        Returns:
            The found Element

        Raises:
            TimeoutError: If element not found within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            element = self.find_by_label(label)
            if element:
                return element
            time.sleep(poll_interval)
        raise TimeoutError(f"Element with label '{label}' not found within {timeout}s")

    def wait_for_element_gone(
        self, accessibility_id: str, timeout: float = 10.0, poll_interval: float = 0.5
    ) -> None:
        """
        Wait until element disappears.

        Args:
            accessibility_id: The accessibility identifier to wait for disappearance
            timeout: Maximum wait time (seconds)
            poll_interval: Time between checks (seconds)

        Raises:
            TimeoutError: If element still present after timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            element = self.find_element(accessibility_id)
            if not element:
                return
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Element '{accessibility_id}' still present after {timeout}s"
        )

    def assert_exists(self, accessibility_id: str, message: str = "") -> Element:
        """
        Assert element exists right now.

        Args:
            accessibility_id: The accessibility identifier to check
            message: Optional custom error message

        Returns:
            The found Element

        Raises:
            ElementNotFoundError: If element not found
        """
        element = self.find_element(accessibility_id)
        if not element:
            msg = message or f"Element '{accessibility_id}' not found"
            raise ElementNotFoundError(msg)
        return element

    def assert_not_exists(self, accessibility_id: str, message: str = "") -> None:
        """
        Assert element does NOT exist right now.

        Args:
            accessibility_id: The accessibility identifier to check
            message: Optional custom error message

        Raises:
            AXeError: If element is found
        """
        element = self.find_element(accessibility_id)
        if element:
            msg = message or f"Element '{accessibility_id}' should not exist but was found"
            raise AXeError(msg)

    def assert_label_contains(self, accessibility_id: str, text: str) -> None:
        """
        Assert element's label contains specific text.

        Args:
            accessibility_id: The accessibility identifier to check
            text: Text that should be in the label

        Raises:
            ElementNotFoundError: If element not found
            AXeError: If label doesn't contain text
        """
        element = self.assert_exists(accessibility_id)
        if element.label is None or text not in element.label:
            raise AXeError(
                f"Element '{accessibility_id}' label '{element.label}' "
                f"does not contain '{text}'"
            )

    def assert_label_equals(self, accessibility_id: str, expected: str) -> None:
        """
        Assert element's label equals specific text.

        Args:
            accessibility_id: The accessibility identifier to check
            expected: Expected label text

        Raises:
            ElementNotFoundError: If element not found
            AXeError: If label doesn't match
        """
        element = self.assert_exists(accessibility_id)
        if element.label != expected:
            raise AXeError(
                f"Element '{accessibility_id}' label '{element.label}' "
                f"does not equal '{expected}'"
            )

    # -------------------------------------------------------------------------
    # App Lifecycle
    # -------------------------------------------------------------------------

    def launch_app(self, bundle_id: str | None = None) -> None:
        """
        Launch the app in the simulator.

        Args:
            bundle_id: Bundle ID to launch. Uses self.app_bundle_id if not provided.

        Raises:
            AXeError: If no bundle ID available or launch fails
        """
        bid = bundle_id or self.app_bundle_id
        if not bid:
            raise AXeError("No bundle ID provided for launch_app")
        cmd = ["xcrun", "simctl", "launch", self.udid, bid]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise AXeError(f"Failed to launch app: {result.stderr}")

    def terminate_app(self, bundle_id: str | None = None) -> None:
        """
        Terminate the app in the simulator.

        Args:
            bundle_id: Bundle ID to terminate. Uses self.app_bundle_id if not provided.

        Raises:
            AXeError: If no bundle ID available
        """
        bid = bundle_id or self.app_bundle_id
        if not bid:
            raise AXeError("No bundle ID provided for terminate_app")
        cmd = ["xcrun", "simctl", "terminate", self.udid, bid]
        subprocess.run(cmd, capture_output=True, text=True)
        # Don't raise on failure - app might not be running

    def press_home(self) -> None:
        """Press the home button to go to home screen."""
        self._run_axe("button", "home")

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def sleep(self, seconds: float) -> None:
        """Sleep for specified duration (convenience method)."""
        time.sleep(seconds)

    def screenshot(self, output_path: str | None = None) -> str:
        """
        Take a screenshot of the simulator.

        Args:
            output_path: Optional path to save screenshot

        Returns:
            Path to the saved screenshot
        """
        # Use xcrun simctl for screenshots (AXe doesn't have this)
        if output_path is None:
            output_path = f"screenshot_{int(time.time())}.png"
        cmd = ["xcrun", "simctl", "io", self.udid, "screenshot", output_path]
        subprocess.run(cmd, check=True)
        return output_path

    def print_ui_tree(self) -> None:
        """Print the current UI hierarchy (for debugging)."""
        result = self._run_axe("describe-ui")
        print(result.stdout)
