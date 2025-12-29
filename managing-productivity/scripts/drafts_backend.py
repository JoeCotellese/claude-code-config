#!/usr/bin/env python3
# ABOUTME: Backend implementation for Drafts app using URL schemes
# ABOUTME: Provides abstract operations (capture, list, search, etc.) via Drafts URL schemes

import subprocess
import urllib.parse
from typing import Optional, List


def _open_url(url: str):
    """Open a URL using macOS 'open' command."""
    subprocess.run(["open", url], check=True)


def capture(text: str, tags: Optional[List[str]] = None, action: Optional[str] = None) -> str:
    """
    Add new item to inbox.

    Args:
        text: The task description
        tags: Optional list of tags (defaults to ['inbox'])
        action: Optional Drafts action to run after creation

    Returns:
        The URL that was opened
    """
    if tags is None:
        tags = ["inbox"]

    tag_string = ",".join(tags)

    params = {
        "text": text,
        "tag": tag_string
    }

    if action:
        params["action"] = action

    url = "drafts://x-callback-url/create?" + urllib.parse.urlencode(params)
    _open_url(url)
    return url


def list_inbox() -> str:
    """
    Open Drafts showing all inbox items.

    Returns:
        The URL that was opened
    """
    url = "drafts://x-callback-url/search?tag=inbox"
    _open_url(url)
    return url


def list_by_context(gtd_list: str) -> str:
    """
    Open Drafts showing items from specific GTD list.

    Args:
        gtd_list: One of 'next-actions', 'projects', 'waiting-for', 'someday-maybe', 'reference'

    Returns:
        The URL that was opened
    """
    url = f"drafts://x-callback-url/search?tag={gtd_list}"
    _open_url(url)
    return url


def search(query: Optional[str] = None, tag: Optional[str] = None) -> str:
    """
    Search for items in Drafts.

    Args:
        query: Text to search for
        tag: Filter by tag

    Returns:
        The URL that was opened
    """
    params = {}
    if query:
        params["query"] = query
    if tag:
        params["tag"] = tag

    url = "drafts://x-callback-url/search?" + urllib.parse.urlencode(params)
    _open_url(url)
    return url


def add_metadata(uuid: str, tags: List[str]) -> str:
    """
    Add tags (context/energy/time metadata) to an item.

    Args:
        uuid: Draft identifier
        tags: List of tags to add

    Returns:
        The URL that was opened
    """
    tag_string = ",".join(tags)
    params = {
        "uuid": uuid,
        "addTags": tag_string
    }

    url = "drafts://x-callback-url/update?" + urllib.parse.urlencode(params)
    _open_url(url)
    return url


def move_to_list(uuid: str, from_list: str, to_list: str) -> str:
    """
    Move item between GTD lists.

    Args:
        uuid: Draft identifier
        from_list: Current GTD list tag
        to_list: Target GTD list tag

    Returns:
        The URL that was opened
    """
    params = {
        "uuid": uuid,
        "removeTags": from_list,
        "addTags": to_list
    }

    url = "drafts://x-callback-url/update?" + urllib.parse.urlencode(params)
    _open_url(url)
    return url


def mark_complete(uuid: str, archive: bool = True) -> str:
    """
    Mark item as complete (archive it).

    Args:
        uuid: Draft identifier
        archive: Whether to archive the draft (default True)

    Returns:
        The URL that was opened
    """
    params = {
        "uuid": uuid,
        "archive": "true" if archive else "false"
    }

    url = "drafts://x-callback-url/update?" + urllib.parse.urlencode(params)
    _open_url(url)
    return url


def get_item(uuid: str) -> str:
    """
    Get details of a single item (opens in Drafts).

    Args:
        uuid: Draft identifier

    Returns:
        The URL that was opened
    """
    url = f"drafts://x-callback-url/get?uuid={uuid}"
    _open_url(url)
    return url


def filter_by_metadata(gtd_list: str, context: Optional[str] = None,
                       energy: Optional[str] = None, time: Optional[str] = None) -> str:
    """
    Filter items by multiple criteria.

    Args:
        gtd_list: GTD list to filter (e.g., 'next-actions')
        context: Context tag (e.g., '@computer')
        energy: Energy tag (e.g., '#energy-medium')
        time: Time tag (e.g., '#time-30m')

    Returns:
        The URL that was opened
    """
    tags = [gtd_list]
    if context:
        tags.append(context)
    if energy:
        tags.append(energy)
    if time:
        tags.append(time)

    tag_string = ",".join(tags)
    url = f"drafts://x-callback-url/search?tag={tag_string}"
    _open_url(url)
    return url


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: drafts_backend.py <operation> [args...]")
        print("\nOperations:")
        print("  capture <text> [tags...]")
        print("  list-inbox")
        print("  list <gtd-list>")
        print("  search [query] [tag]")
        print("  add-metadata <uuid> <tag1> [tag2...]")
        print("  move <uuid> <from-list> <to-list>")
        print("  complete <uuid>")
        print("  get <uuid>")
        print("  filter <gtd-list> [context] [energy] [time]")
        sys.exit(1)

    operation = sys.argv[1]

    if operation == "capture":
        text = sys.argv[2]
        tags = sys.argv[3:] if len(sys.argv) > 3 else None
        url = capture(text, tags)
        print(f"Created: {url}")

    elif operation == "list-inbox":
        url = list_inbox()
        print(f"Opened: {url}")

    elif operation == "list":
        gtd_list = sys.argv[2]
        url = list_by_context(gtd_list)
        print(f"Opened: {url}")

    elif operation == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        tag = sys.argv[3] if len(sys.argv) > 3 else None
        url = search(query, tag)
        print(f"Opened: {url}")

    elif operation == "add-metadata":
        uuid = sys.argv[2]
        tags = sys.argv[3:]
        url = add_metadata(uuid, tags)
        print(f"Updated: {url}")

    elif operation == "move":
        uuid = sys.argv[2]
        from_list = sys.argv[3]
        to_list = sys.argv[4]
        url = move_to_list(uuid, from_list, to_list)
        print(f"Moved: {url}")

    elif operation == "complete":
        uuid = sys.argv[2]
        url = mark_complete(uuid)
        print(f"Completed: {url}")

    elif operation == "get":
        uuid = sys.argv[2]
        url = get_item(uuid)
        print(f"Opened: {url}")

    elif operation == "filter":
        gtd_list = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else None
        energy = sys.argv[4] if len(sys.argv) > 4 else None
        time = sys.argv[5] if len(sys.argv) > 5 else None
        url = filter_by_metadata(gtd_list, context, energy, time)
        print(f"Filtered: {url}")

    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)
