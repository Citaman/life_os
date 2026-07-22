"""Add and backfill the Notion ``Nature du coût`` transaction property.

The migration is intentionally narrow: it only writes the new select property.
Income and internal transfers stay blank because they are not costs. Existing
non-empty values are preserved unless ``--force`` is explicitly supplied.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import Counter
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

from convert_sg_exports_to_transactions import classify_cost_nature
from import_transactions_to_notion import (
    ACCOUNT_DATA_SOURCES,
    ensure_cost_nature_property,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill Nature du coût in Notion transactions.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without mutating Notion.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing non-empty Nature du coût values. Disabled by default.",
    )
    return parser.parse_args()


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} missing in env.")
    return value


def plain_text(prop: dict[str, Any], kind: str) -> str:
    return "".join(part.get("plain_text", "") for part in prop.get(kind, []))


def text_value(properties: dict[str, Any], name: str) -> str:
    prop = properties.get(name, {})
    kind = prop.get("type")
    if kind in {"rich_text", "title"}:
        return plain_text(prop, kind)
    return ""


def select_value(properties: dict[str, Any], name: str) -> str:
    return (properties.get(name, {}).get("select") or {}).get("name") or ""


def query_pages(client: Client, data_source_id: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"data_source_id": data_source_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        response = client.data_sources.query(**payload)
        pages.extend(response.get("results", []))
        if not response.get("has_more"):
            return pages
        cursor = response.get("next_cursor")


def desired_nature(properties: dict[str, Any]) -> str:
    amount = properties.get("Montant", {}).get("number")
    if amount is None:
        return "À vérifier"
    return classify_cost_nature(
        amount=float(amount),
        category=text_value(properties, "Catégorie"),
        subcategory=text_value(properties, "Sous-catégorie"),
        merchant=text_value(properties, "Marchand"),
        recurring=bool(properties.get("Récurrent", {}).get("checkbox")),
        internal=bool(properties.get("Interne", {}).get("checkbox")),
    )


def backfill_account(
    client: Client,
    data_source_id: str,
    account_name: str,
    *,
    dry_run: bool,
    force: bool,
) -> tuple[int, int]:
    ensure_cost_nature_property(client, data_source_id, account_name, dry_run=dry_run)
    pages = query_pages(client, data_source_id)
    updates: list[tuple[str, str]] = []
    desired_counts: Counter[str] = Counter()
    unresolved_merchants: Counter[str] = Counter()
    preserved = 0

    for page in pages:
        properties = page.get("properties", {})
        desired = desired_nature(properties)
        if not desired:
            continue
        desired_counts[desired] += 1
        if desired == "À vérifier":
            unresolved_merchants[text_value(properties, "Marchand") or "Sans marchand"] += 1
        existing = select_value(properties, "Nature du coût")
        if existing == desired:
            continue
        if existing and not force:
            preserved += 1
            continue
        page_id = page.get("id")
        if page_id:
            updates.append((page_id, desired))

    action = "would update" if dry_run else "to update"
    print(f"{account_name}: {len(pages)} pages, {len(updates)} {action}, {preserved} preserved")
    print(
        "  classification: "
        + ", ".join(f"{name}={count}" for name, count in sorted(desired_counts.items()))
    )
    if unresolved_merchants:
        top = ", ".join(
            f"{merchant}={count}"
            for merchant, count in unresolved_merchants.most_common(8)
        )
        print(f"  à vérifier (top): {top}")

    if not dry_run:
        for index, (page_id, nature) in enumerate(updates, start=1):
            client.pages.update(
                page_id=page_id,
                properties={"Nature du coût": {"select": {"name": nature}}},
            )
            if index % 50 == 0 or index == len(updates):
                print(f"  updated {index}/{len(updates)}")
            time.sleep(0.12)

    return len(pages), len(updates)


def main() -> None:
    load_dotenv()
    args = parse_args()
    client = Client(auth=require_env("NOTION_TOKEN"))
    total_pages = 0
    total_updates = 0

    for account_name, env_name in ACCOUNT_DATA_SOURCES.items():
        pages, updates = backfill_account(
            client,
            require_env(env_name),
            account_name,
            dry_run=args.dry_run,
            force=args.force,
        )
        total_pages += pages
        total_updates += updates

    suffix = " (dry-run, no mutations)" if args.dry_run else ""
    print(f"Cost nature backfill complete: {total_pages} pages, {total_updates} updates{suffix}.")


if __name__ == "__main__":
    main()
