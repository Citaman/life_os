"""Helper: list all child blocks of a Notion page with their ID + type + short text snippet.

Usage:
    python scripts/inspect_notion.py PAGE_ID
"""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
client = Client(auth=os.environ["NOTION_TOKEN"])


def block_text(b: dict) -> str:
    t = b["type"]
    body = b.get(t) or {}
    if isinstance(body, dict) and "rich_text" in body:
        return "".join(r.get("plain_text", "") for r in body["rich_text"])[:80]
    if t == "embed":
        return body.get("url", "")[:80]
    if t == "bookmark":
        return body.get("url", "")[:80]
    return ""


def walk(page_id: str, indent: int = 0) -> None:
    cursor = None
    while True:
        payload = {"block_id": page_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.blocks.children.list(**payload)
        for b in resp["results"]:
            pad = "  " * indent
            print(f"{pad}[{b['type']:18s}] {b['id'][:8]} · {block_text(b)}")
            if b.get("has_children") and b["type"] in {"toggle", "callout", "column_list", "column"}:
                walk(b["id"], indent + 1)
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/inspect_notion.py PAGE_ID")
    walk(sys.argv[1])


if __name__ == "__main__":
    main()
