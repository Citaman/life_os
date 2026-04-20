"""
Fetch all 3 Notion databases and save raw pages to data/raw_notion.json.

DBs:
- Plan d'exécution (achievements, sous-achievements, tâches atomiques)
- Habitudes (weekly tracker)
- Backlog Vie (master intentions register)

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

TOKEN = os.environ.get("NOTION_TOKEN")
if not TOKEN:
    sys.exit("ERROR: NOTION_TOKEN missing in env.")

PLAN_DS = os.environ["PLAN_DS"]
HABITUDES_DS = os.environ["HABITUDES_DS"]
BACKLOG_DS = os.environ["BACKLOG_DS"]

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
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(bundle, indent=2, ensure_ascii=False))
    counts = {k: len(v) for k, v in bundle.items()}
    print(f"Wrote {OUT_PATH} — {counts}")


if __name__ == "__main__":
    main()
