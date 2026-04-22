"""
Import categorized consolidated transactions into 2 Notion data sources:
- Transactions Anthonny
- Transactions Mirane

The import is idempotent on the custom "Source clé" property.

Usage:
    python scripts/import_transactions_to_notion.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

TOKEN = os.environ.get("NOTION_TOKEN")
if not TOKEN:
    sys.exit("ERROR: NOTION_TOKEN missing in env.")

ANTHONNY_DS = os.environ.get("TX_ANTHONNY_DS", "97850d4c-fded-47ed-9e08-15031b699023")
MIRANE_DS = os.environ.get("TX_MIRANE_DS", "6ab9ce1a-fae9-41ff-9d9e-350bbd8d9596")

CSV_PATH = Path("/Users/anthonny.olime/Downloads/Data/Financial/processed_2026-04/consolidated_transactions.csv")

client = Client(auth=TOKEN)


def source_key(row: dict[str, str]) -> str:
    raw = "||".join(
        [
            row.get("account", ""),
            row.get("date", ""),
            row.get("amount", ""),
            row.get("direction", ""),
            row.get("merchant", ""),
            row.get("libelle", ""),
            row.get("detail", ""),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def title_of(row: dict[str, str]) -> str:
    amount = row.get("amount", "")
    merchant = row.get("merchant", "") or "Sans marchand"
    return f"{row.get('date', '')} · {merchant} · {amount}"[:180]


def text_prop(value: str) -> list[dict[str, Any]]:
    if not value:
        return []
    return [{"type": "text", "text": {"content": value[:2000]}}]


def query_existing_keys(data_source_id: str) -> set[str]:
    keys: set[str] = set()
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"data_source_id": data_source_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.data_sources.query(**payload)
        for page in resp.get("results", []):
            prop = page.get("properties", {}).get("Source clé", {})
            rich_text = prop.get("rich_text", [])
            if rich_text:
                keys.add("".join(part.get("plain_text", "") for part in rich_text))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return keys


def page_payload(data_source_id: str, row: dict[str, str]) -> dict[str, Any]:
    recurring = row.get("is_recurring", "") == "Y"
    internal = row.get("is_internal", "") == "Y"
    auto = row.get("auto_categorized", "") == "Y"
    return {
        "parent": {"type": "data_source_id", "data_source_id": data_source_id},
        "properties": {
            "Transaction": {"title": text_prop(title_of(row))},
            "Date": {"date": {"start": row["date"]}},
            "Mois clé": {"rich_text": text_prop(row["date"][:7])},
            "Montant": {"number": float(row["amount"])},
            "Direction": {"select": {"name": row["direction"]}},
            "Marchand": {"rich_text": text_prop(row.get("merchant", ""))},
            "Catégorie": {"select": {"name": row.get("category", "Uncategorized")}},
            "Sous-catégorie": {"select": {"name": row.get("subcategory", "Unknown")}},
            "Récurrent": {"checkbox": recurring},
            "Interne": {"checkbox": internal},
            "Auto catégorisé": {"checkbox": auto},
            "Libellé": {"rich_text": text_prop(row.get("libelle", ""))},
            "Détail": {"rich_text": text_prop(row.get("detail", ""))},
            "Source clé": {"rich_text": text_prop(source_key(row))},
        },
    }


def create_missing_rows(data_source_id: str, account_name: str, rows: list[dict[str, str]]) -> None:
    existing = query_existing_keys(data_source_id)
    pending = [row for row in rows if source_key(row) not in existing]
    print(f"{account_name}: {len(existing)} existing, {len(pending)} missing")

    for idx, row in enumerate(pending, start=1):
        client.pages.create(**page_payload(data_source_id, row))
        if idx % 25 == 0 or idx == len(pending):
            print(f"  created {idx}/{len(pending)}")
        time.sleep(0.12)


def main() -> None:
    if not CSV_PATH.exists():
        sys.exit(f"ERROR: missing CSV {CSV_PATH}")

    rows_by_account: dict[str, list[dict[str, str]]] = {"Anthonny": [], "Mirane": []}
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            account = row.get("account", "")
            if account in rows_by_account:
                rows_by_account[account].append(row)

    create_missing_rows(ANTHONNY_DS, "Anthonny", rows_by_account["Anthonny"])
    create_missing_rows(MIRANE_DS, "Mirane", rows_by_account["Mirane"])
    print("Transaction import complete.")


if __name__ == "__main__":
    main()
