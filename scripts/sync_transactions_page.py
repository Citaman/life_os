"""
Append the live transaction embeds to the dedicated Notion page if missing.

Idempotent enough for reruns:
- keeps existing non-target blocks untouched
- only appends missing target embeds
- only appends the section heading once

Usage:
    python scripts/sync_transactions_page.py
    python scripts/sync_transactions_page.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

EMBEDS: list[tuple[str, str]] = [
    ("Treemap dépenses · Anthonny", "treemap-transactions-account-anthonny"),
    ("Historique dépenses · Anthonny", "history-transactions-account-anthonny"),
    ("Treemap dépenses · Mirane", "treemap-transactions-account-mirane"),
    ("Historique dépenses · Mirane", "history-transactions-account-mirane"),
]

SECTION_HEADING = "Visuels transactions live"


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} missing in env.")
    return value


def require_base_url() -> str:
    value = os.environ.get("TRANSACTIONS_BASE_URL") or os.environ.get("BASE_URL")
    if not value:
        sys.exit(
            "ERROR: TRANSACTIONS_BASE_URL missing in env. "
            "BASE_URL is also accepted as a fallback env name. "
            "Set it to the published life_os base URL, for example https://example.com/life_os."
        )
    return value.rstrip("/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append missing live transaction embeds to the configured Notion page."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read the Notion page and print what would be appended without mutating Notion.",
    )
    return parser.parse_args()


def list_top_level_blocks(client: Client, page_id: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"block_id": page_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.blocks.children.list(**payload)
        blocks.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks


def rich_text_plain(block: dict[str, Any], kind: str) -> str:
    payload = block.get(kind, {})
    return "".join(item.get("plain_text", "") for item in payload.get("rich_text", []))


def make_divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def make_heading_2(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def make_heading_3(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def make_paragraph(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def make_embed(url: str, caption: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "embed",
        "embed": {
            "url": url,
            "caption": [{"type": "text", "text": {"content": caption}}],
        },
    }


def main() -> None:
    load_dotenv()
    args = parse_args()
    token = require_env("NOTION_TOKEN")
    base_url = require_base_url()
    transactions_page_id = require_env("PAGE_TRANSACTIONS_REAL")
    client = Client(auth=token)

    blocks = list_top_level_blocks(client, transactions_page_id)
    existing_urls = {
        block.get("embed", {}).get("url")
        for block in blocks
        if block.get("type") == "embed"
    }
    has_heading = any(
        block.get("type") == "heading_2" and rich_text_plain(block, "heading_2") == SECTION_HEADING
        for block in blocks
    )

    children: list[dict[str, Any]] = []
    if not has_heading:
        children.extend(
            [
                make_divider(),
                make_heading_2(SECTION_HEADING),
                make_paragraph(
                    "Ces visuels se régénèrent depuis life_os. Le treemap permet de changer de mois par compte, et l'historique montre les catégories réelles dans le temps."
                ),
            ]
        )

    added = 0
    for title, slug in EMBEDS:
        url = f"{base_url}/{slug}.html"
        if url in existing_urls:
            continue
        children.append(make_heading_3(title))
        children.append(make_embed(url, title))
        added += 1

    if not children:
        print("Transactions page already up to date.")
        return

    if args.dry_run:
        print(
            "Transactions page would be updated: "
            f"{added} embed(s), {len(children)} block(s) appended. No mutation performed."
        )
        return

    client.blocks.children.append(block_id=transactions_page_id, children=children)
    print(f"Transactions page updated: {added} embed(s) added.")


if __name__ == "__main__":
    main()
