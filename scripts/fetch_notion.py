"""
Fetch core Notion databases and optional finance databases into data/raw_notion.json.

Core DBs:
- Plan d'exécution (achievements, sous-achievements, tâches atomiques)
- Habitudes (weekly tracker)
- Backlog Vie (master intentions register)

Optional finance DBs:
- Finance mensuelle
- Lignes budget mensuel
- Journal Pro & Financier
- Transactions Anthonny / Mirane
- Transactions Compte joint

Usage:
    python scripts/fetch_notion.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()


def env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def require_env(*names: str) -> dict[str, str]:
    values = {name: env_value(name) for name in names}
    missing = [name for name, value in values.items() if value is None]
    if missing:
        missing_list = ", ".join(missing)
        sys.exit(
            f"ERROR: missing required env value(s): {missing_list}.\n"
            "Set them in .env or export them before running scripts/fetch_notion.py."
        )
    return {name: value for name, value in values.items() if value is not None}


required_env = require_env("NOTION_TOKEN", "PLAN_DS", "HABITUDES_DS", "BACKLOG_DS")
TOKEN = required_env["NOTION_TOKEN"]
PLAN_DS = required_env["PLAN_DS"]
HABITUDES_DS = required_env["HABITUDES_DS"]
BACKLOG_DS = required_env["BACKLOG_DS"]
FINANCE_MONTHLY_DS = env_value("FINANCE_MONTHLY_DS")
BUDGET_LINES_DS = env_value("BUDGET_LINES_DS")
PRO_FI_JOURNAL_DS = env_value("PRO_FI_JOURNAL_DS")
TX_ANTHONNY_DS = env_value("TX_ANTHONNY_DS")
TX_MIRANE_DS = env_value("TX_MIRANE_DS")
TX_JOINT_DS = env_value("TX_JOINT_DS")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "data" / "raw_notion.json"

client = Client(auth=TOKEN)


def query_data_source(data_source_id: str) -> list[dict[str, Any]]:
    """Paginate through a Notion data source and return all pages."""
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    page_num = 0
    while True:
        payload: dict[str, Any] = {"data_source_id": data_source_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.data_sources.query(**payload)
        page_num += 1
        batch = resp.get("results", [])
        pages.extend(batch)
        print(f"  page {page_num}: +{len(batch)} (total {len(pages)})")
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return pages


def extract_prop(props: dict[str, Any], name: str) -> Any:
    """Read a property value in a normalized form."""
    if name not in props:
        return None
    p = props[name]
    kind = p.get("type")
    if kind == "title":
        return "".join(t.get("plain_text", "") for t in p.get("title", []))
    if kind == "rich_text":
        return "".join(t.get("plain_text", "") for t in p.get("rich_text", []))
    if kind == "select":
        v = p.get("select")
        return v.get("name") if v else None
    if kind == "status":
        v = p.get("status")
        return v.get("name") if v else None
    if kind == "multi_select":
        return [v["name"] for v in p.get("multi_select", [])]
    if kind == "number":
        return p.get("number")
    if kind == "checkbox":
        return p.get("checkbox")
    if kind == "date":
        d = p.get("date")
        if not d:
            return None
        return {"start": d.get("start"), "end": d.get("end")}
    if kind == "relation":
        return [r["id"] for r in p.get("relation", [])]
    if kind == "formula":
        f = p.get("formula", {})
        return f.get(f.get("type"))
    if kind == "created_time":
        return p.get("created_time")
    return None


def simplify(raw_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for page in raw_pages:
        props = page.get("properties", {})
        simple: dict[str, Any] = {
            "id": page["id"],
            "url": page.get("url"),
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time"),
        }
        for prop_name in props:
            simple[prop_name] = extract_prop(props, prop_name)
        out.append(simple)
    return out


def main() -> None:
    print("Fetching Plan d'exécution...")
    plan_raw = query_data_source(PLAN_DS)
    print(f"Plan total: {len(plan_raw)} pages\n")

    print("Fetching Habitudes...")
    hab_raw = query_data_source(HABITUDES_DS)
    print(f"Habitudes total: {len(hab_raw)} pages\n")

    print("Fetching Backlog Vie...")
    backlog_raw = query_data_source(BACKLOG_DS)
    print(f"Backlog total: {len(backlog_raw)} pages\n")

    bundle = {
        "plan_execution": simplify(plan_raw),
        "habitudes": simplify(hab_raw),
        "backlog_vie": simplify(backlog_raw),
        "finance_monthly": [],
        "budget_lines": [],
        "pro_fi_journal": [],
        "transactions_anthonny": [],
        "transactions_mirane": [],
        "transactions_joint": [],
    }

    if FINANCE_MONTHLY_DS:
        print("Fetching Finance mensuelle...")
        finance_raw = query_data_source(FINANCE_MONTHLY_DS)
        bundle["finance_monthly"] = simplify(finance_raw)
        print(f"Finance mensuelle total: {len(finance_raw)} pages\n")
    else:
        print("Skipping Finance mensuelle (FINANCE_MONTHLY_DS not set).\n")

    if BUDGET_LINES_DS:
        print("Fetching Lignes budget mensuel...")
        budget_lines_raw = query_data_source(BUDGET_LINES_DS)
        bundle["budget_lines"] = simplify(budget_lines_raw)
        print(f"Lignes budget mensuel total: {len(budget_lines_raw)} pages\n")
    else:
        print("Skipping Lignes budget mensuel (BUDGET_LINES_DS not set).\n")

    if PRO_FI_JOURNAL_DS:
        print("Fetching Journal Pro & Financier...")
        journal_raw = query_data_source(PRO_FI_JOURNAL_DS)
        bundle["pro_fi_journal"] = simplify(journal_raw)
        print(f"Journal Pro & Financier total: {len(journal_raw)} pages\n")
    else:
        print("Skipping Journal Pro & Financier (PRO_FI_JOURNAL_DS not set).\n")

    if TX_ANTHONNY_DS:
        print("Fetching Transactions Anthonny...")
        tx_anthonny_raw = query_data_source(TX_ANTHONNY_DS)
        bundle["transactions_anthonny"] = simplify(tx_anthonny_raw)
        print(f"Transactions Anthonny total: {len(tx_anthonny_raw)} pages\n")
    else:
        print("Skipping Transactions Anthonny (TX_ANTHONNY_DS not set).\n")

    if TX_MIRANE_DS:
        print("Fetching Transactions Mirane...")
        tx_mirane_raw = query_data_source(TX_MIRANE_DS)
        bundle["transactions_mirane"] = simplify(tx_mirane_raw)
        print(f"Transactions Mirane total: {len(tx_mirane_raw)} pages\n")
    else:
        print("Skipping Transactions Mirane (TX_MIRANE_DS not set).\n")

    if TX_JOINT_DS:
        print("Fetching Transactions Compte joint...")
        tx_joint_raw = query_data_source(TX_JOINT_DS)
        bundle["transactions_joint"] = simplify(tx_joint_raw)
        print(f"Transactions Compte joint total: {len(tx_joint_raw)} pages\n")
    else:
        print("Skipping Transactions Compte joint (TX_JOINT_DS not set).\n")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(bundle, indent=2, ensure_ascii=False))
    counts = {k: len(v) for k, v in bundle.items()}
    print(f"Wrote {OUT_PATH} — {counts}")


if __name__ == "__main__":
    main()
