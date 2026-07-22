"""Categorize only unresolved transaction rows already stored in Notion.

This is a narrow cleanup pass: rows with a meaningful category and
subcategory are never touched. Merchant rules are shared with the SG converter.

Usage:
    python scripts/fix_uncategorized_transactions.py --dry-run
    python scripts/fix_uncategorized_transactions.py
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

if __package__:
    from .convert_sg_exports_to_transactions import classify
else:
    from convert_sg_exports_to_transactions import classify


ACCOUNT_DATA_SOURCES = {
    "Anthonny": "TX_ANTHONNY_DS",
    "Mirane": "TX_MIRANE_DS",
    "Joint": "TX_JOINT_DS",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Categorize unresolved Notion transactions only.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without mutating Notion.")
    return parser.parse_args()


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} missing in env.")
    return value


def plain_text(prop: dict[str, Any], kind: str) -> str:
    return "".join(part.get("plain_text", "") for part in prop.get(kind, []))


def text_value(properties: dict[str, Any], name: str) -> str:
    return plain_text(properties.get(name, {}), "rich_text")


def is_unresolved(properties: dict[str, Any]) -> bool:
    category = text_value(properties, "Catégorie")
    subcategory = text_value(properties, "Sous-catégorie")
    return not category or category == "Uncategorized" or not subcategory or subcategory == "Unknown"


def text_payload(value: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": value[:2000]}}] if value else []


def query_pages(client: Client, data_source_id: str) -> list[dict[str, Any]]:
    pages = []
    cursor = None
    while True:
        payload: dict[str, Any] = {"data_source_id": data_source_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        response = client.data_sources.query(**payload)
        pages.extend(response.get("results", []))
        if not response.get("has_more"):
            return pages
        cursor = response.get("next_cursor")


def cleanup_account(
    client: Client,
    data_source_id: str,
    account: str,
    *,
    dry_run: bool,
) -> tuple[int, int]:
    unresolved = 0
    updated = 0
    for page in query_pages(client, data_source_id):
        properties = page.get("properties", {})
        if not is_unresolved(properties):
            continue
        unresolved += 1

        date_value = (properties.get("Date", {}).get("date") or {}).get("start")
        amount = properties.get("Montant", {}).get("number")
        if not date_value or amount is None:
            print(f"WARNING: {account} page {page.get('id')} lacks date or amount; skipped.")
            continue

        converted = classify(
            {
                "date": date_value,
                "amount": amount,
                "libelle": text_value(properties, "Libellé"),
                "detail": text_value(properties, "Détail"),
            },
            account,
        )
        print(
            f"{account} {date_value} {amount:.2f}: "
            f"{converted['merchant']} -> {converted['category']} / {converted['subcategory']}"
        )
        if dry_run:
            updated += 1
            continue

        client.pages.update(
            page_id=page["id"],
            properties={
                "Marchand": {"rich_text": text_payload(converted["merchant"])},
                "Catégorie": {"rich_text": text_payload(converted["category"])},
                "Sous-catégorie": {"rich_text": text_payload(converted["subcategory"])},
                "Récurrent": {"checkbox": converted["is_recurring"] == "Y"},
                "Auto catégorisé": {"checkbox": True},
            },
        )
        updated += 1
        time.sleep(0.12)
    return unresolved, updated


def main() -> None:
    load_dotenv()
    args = parse_args()
    client = Client(auth=require_env("NOTION_TOKEN"))
    total_unresolved = 0
    total_updated = 0
    for account, env_name in ACCOUNT_DATA_SOURCES.items():
        unresolved, updated = cleanup_account(
            client,
            require_env(env_name),
            account,
            dry_run=args.dry_run,
        )
        total_unresolved += unresolved
        total_updated += updated
        print(f"{account}: {unresolved} unresolved, {updated} {'would update' if args.dry_run else 'updated'}")

    suffix = " (dry-run, no mutations)" if args.dry_run else ""
    print(f"Cleanup complete: {total_unresolved} unresolved, {total_updated} handled{suffix}.")


if __name__ == "__main__":
    main()
