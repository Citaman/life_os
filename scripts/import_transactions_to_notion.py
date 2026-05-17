"""
Import categorized consolidated transactions into 3 Notion data sources:
- Transactions Anthonny
- Transactions Mirane
- Transactions Compte joint

The import is idempotent on the custom "Source clé" property.

Usage:
    python scripts/import_transactions_to_notion.py --csv data/consolidated_transactions.csv
    python scripts/import_transactions_to_notion.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

REQUIRED_COLUMNS = {
    "account",
    "date",
    "amount",
    "direction",
    "merchant",
    "category",
    "subcategory",
    "is_recurring",
    "is_internal",
    "auto_categorized",
    "libelle",
    "detail",
}

ACCOUNT_DATA_SOURCES = {
    "Anthonny": "TX_ANTHONNY_DS",
    "Mirane": "TX_MIRANE_DS",
    "Joint": "TX_JOINT_DS",
}

RICH_TEXT_PROPERTIES = {
    "Mois clé",
    "Direction",
    "Marchand",
    "Catégorie",
    "Sous-catégorie",
    "Libellé",
    "Détail",
    "Source clé",
}


@dataclass(frozen=True)
class ExistingPage:
    page_id: str
    values: dict[str, Any]


@dataclass(frozen=True)
class ExistingPages:
    by_source_key: dict[str, ExistingPage]
    by_identity_key: dict[str, ExistingPage]


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


def identity_amount(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value or "")


def identity_key(values: dict[str, Any]) -> str:
    raw = "||".join(
        [
            str(values.get("Date") or values.get("date") or ""),
            identity_amount(values.get("Montant", values.get("amount", ""))),
            str(values.get("Direction") or values.get("direction") or ""),
            str(values.get("Libellé") or values.get("libelle") or ""),
            str(values.get("Détail") or values.get("detail") or ""),
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


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} missing in env.")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upsert categorized consolidated transactions into Notion data sources."
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        help="Path to consolidated_transactions.csv. Defaults to TRANSACTIONS_CSV_PATH.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read CSV and Notion, then print create/update counts without mutating Notion.",
    )
    return parser.parse_args()


def resolve_csv_path(cli_path: str | None) -> Path:
    raw_path = cli_path or os.environ.get("TRANSACTIONS_CSV_PATH")
    if not raw_path:
        sys.exit(
            "ERROR: CSV path missing. Pass --csv /path/to/consolidated_transactions.csv "
            "or set TRANSACTIONS_CSV_PATH in env."
        )

    csv_path = Path(raw_path).expanduser()
    if not csv_path.exists():
        sys.exit(f"ERROR: CSV file not found: {csv_path}")
    if not csv_path.is_file():
        sys.exit(f"ERROR: CSV path is not a file: {csv_path}")
    return csv_path


def parse_amount(value: str, line_number: int) -> float:
    try:
        return float(value)
    except ValueError:
        sys.exit(f"ERROR: invalid amount on CSV line {line_number}: {value!r}")


def validate_date(value: str, line_number: int) -> None:
    try:
        date.fromisoformat(value)
    except ValueError:
        sys.exit(f"ERROR: invalid ISO date on CSV line {line_number}: {value!r}")


def validate_csv_columns(fieldnames: list[str] | None, csv_path: Path) -> None:
    if not fieldnames:
        sys.exit(f"ERROR: CSV has no header row: {csv_path}")

    missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if missing:
        sys.exit(
            "ERROR: CSV missing required column(s): "
            f"{', '.join(missing)}. File: {csv_path}"
        )


def read_rows(csv_path: Path) -> dict[str, list[dict[str, str]]]:
    rows_by_account: dict[str, list[dict[str, str]]] = {
        account: [] for account in ACCOUNT_DATA_SOURCES
    }
    seen_keys: dict[str, set[str]] = {account: set() for account in ACCOUNT_DATA_SOURCES}

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        validate_csv_columns(reader.fieldnames, csv_path)

        for line_number, raw_row in enumerate(reader, start=2):
            row = {
                key: (value or "")
                for key, value in raw_row.items()
                if key is not None
            }
            account = row.get("account", "")
            if account not in rows_by_account:
                sys.exit(
                    f"ERROR: unsupported account on CSV line {line_number}: {account!r}. "
                    f"Expected one of: {', '.join(rows_by_account)}"
                )
            if not row.get("date"):
                sys.exit(f"ERROR: missing date on CSV line {line_number}.")
            if not row.get("amount"):
                sys.exit(f"ERROR: missing amount on CSV line {line_number}.")

            validate_date(row["date"], line_number)
            parse_amount(row["amount"], line_number)
            key = source_key(row)
            if key in seen_keys[account]:
                sys.exit(
                    f"ERROR: duplicate Source clé generated in CSV for {account} "
                    f"on line {line_number}: {key}"
                )
            seen_keys[account].add(key)
            rows_by_account[account].append(row)

    return rows_by_account


def plain_text(prop: dict[str, Any], kind: str) -> str:
    return "".join(part.get("plain_text", "") for part in prop.get(kind, []))


def notion_value(properties: dict[str, Any], name: str) -> Any:
    prop = properties.get(name, {})
    if name == "Transaction":
        return plain_text(prop, "title")
    if name == "Date":
        return (prop.get("date") or {}).get("start")
    if name == "Montant":
        return prop.get("number")
    if name in {"Récurrent", "Interne", "Auto catégorisé"}:
        return prop.get("checkbox")
    if name in RICH_TEXT_PROPERTIES:
        return plain_text(prop, "rich_text")
    return None


def query_existing_pages(client: Client, data_source_id: str, account_name: str) -> ExistingPages:
    pages_by_source_key: dict[str, ExistingPage] = {}
    pages_by_identity_key: dict[str, ExistingPage] = {}
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"data_source_id": data_source_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.data_sources.query(**payload)
        for page in resp.get("results", []):
            properties = page.get("properties", {})
            key = notion_value(properties, "Source clé")
            page_id = page.get("id")
            if not page_id:
                continue
            existing_page = ExistingPage(
                page_id=page_id,
                values={name: notion_value(properties, name) for name in desired_value_names()},
            )
            if key:
                if key in pages_by_source_key:
                    print(f"WARNING: duplicate Source clé in {account_name}: {key}; keeping first page.")
                else:
                    pages_by_source_key[key] = existing_page
            natural_key = identity_key(existing_page.values)
            if natural_key in pages_by_identity_key:
                print(f"WARNING: duplicate transaction identity in {account_name}: {natural_key}; keeping first page.")
            else:
                pages_by_identity_key[natural_key] = existing_page
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return ExistingPages(by_source_key=pages_by_source_key, by_identity_key=pages_by_identity_key)


def desired_value_names() -> tuple[str, ...]:
    return (
        "Transaction",
        "Date",
        "Mois clé",
        "Montant",
        "Direction",
        "Marchand",
        "Catégorie",
        "Sous-catégorie",
        "Récurrent",
        "Interne",
        "Auto catégorisé",
        "Libellé",
        "Détail",
        "Source clé",
    )


def desired_values(row: dict[str, str]) -> dict[str, Any]:
    recurring = row.get("is_recurring", "") == "Y"
    internal = row.get("is_internal", "") == "Y"
    auto = row.get("auto_categorized", "") == "Y"
    return {
        "Transaction": title_of(row),
        "Date": row["date"],
        "Mois clé": row["date"][:7],
        "Montant": float(row["amount"]),
        "Direction": row.get("direction", ""),
        "Marchand": row.get("merchant", ""),
        "Catégorie": row.get("category", "Uncategorized"),
        "Sous-catégorie": row.get("subcategory", "Unknown"),
        "Récurrent": recurring,
        "Interne": internal,
        "Auto catégorisé": auto,
        "Libellé": row.get("libelle", ""),
        "Détail": row.get("detail", ""),
        "Source clé": source_key(row),
    }


def property_payload(values: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name, value in values.items():
        if name == "Transaction":
            payload[name] = {"title": text_prop(str(value))}
        elif name == "Date":
            payload[name] = {"date": {"start": str(value)}}
        elif name == "Montant":
            payload[name] = {"number": float(value)}
        elif name in {"Récurrent", "Interne", "Auto catégorisé"}:
            payload[name] = {"checkbox": bool(value)}
        elif name in RICH_TEXT_PROPERTIES:
            payload[name] = {"rich_text": text_prop(str(value))}
        else:
            raise ValueError(f"Unsupported property: {name}")
    return payload


def changed_values(existing: dict[str, Any], desired: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for name, desired_value in desired.items():
        existing_value = existing.get(name)
        if name == "Montant":
            if existing_value is None or abs(float(existing_value) - desired_value) > 0.000001:
                changes[name] = desired_value
            continue
        if existing_value != desired_value:
            changes[name] = desired_value
    return changes


def page_payload(data_source_id: str, row: dict[str, str]) -> dict[str, Any]:
    return {
        "parent": {"type": "data_source_id", "data_source_id": data_source_id},
        "properties": property_payload(desired_values(row)),
    }


def upsert_rows(
    client: Client,
    data_source_id: str,
    account_name: str,
    rows: list[dict[str, str]],
    *,
    dry_run: bool,
) -> None:
    existing = query_existing_pages(client, data_source_id, account_name)
    creates: list[dict[str, str]] = []
    updates: list[tuple[ExistingPage, dict[str, Any]]] = []

    for row in rows:
        key = source_key(row)
        values = desired_values(row)
        page = existing.by_source_key.get(key) or existing.by_identity_key.get(identity_key(values))
        if not page:
            creates.append(row)
            continue
        changes = changed_values(page.values, values)
        if changes:
            updates.append((page, changes))

    create_label = "would create" if dry_run else "to create"
    update_label = "would update" if dry_run else "to update"
    print(
        f"{account_name}: {len(existing.by_identity_key)} existing, "
        f"{len(creates)} {create_label}, {len(updates)} {update_label}"
    )

    if dry_run:
        if updates:
            changed_names = sorted({name for _, changes in updates for name in changes})
            print(f"  changed property set: {', '.join(changed_names)}")
        return

    for idx, row in enumerate(creates, start=1):
        client.pages.create(**page_payload(data_source_id, row))
        if idx % 25 == 0 or idx == len(creates):
            print(f"  created {idx}/{len(creates)}")
        time.sleep(0.12)

    for idx, (page, changes) in enumerate(updates, start=1):
        client.pages.update(page_id=page.page_id, properties=property_payload(changes))
        if idx % 25 == 0 or idx == len(updates):
            print(f"  updated {idx}/{len(updates)}")
        time.sleep(0.12)


def main() -> None:
    load_dotenv()
    args = parse_args()
    csv_path = resolve_csv_path(args.csv_path)
    token = require_env("NOTION_TOKEN")
    data_sources = {
        account: require_env(env_name)
        for account, env_name in ACCOUNT_DATA_SOURCES.items()
    }

    rows_by_account = read_rows(csv_path)
    client = Client(auth=token)

    for account_name, rows in rows_by_account.items():
        upsert_rows(
            client,
            data_sources[account_name],
            account_name,
            rows,
            dry_run=args.dry_run,
        )

    suffix = " (dry-run, no mutations)" if args.dry_run else ""
    print(f"Transaction import complete{suffix}.")


if __name__ == "__main__":
    main()
