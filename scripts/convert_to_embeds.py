"""
LEGACY one-shot migration script.

V2.3-D · Convert static Notion KPI callouts into iframe embeds pointing to live-regenerated HTMLs.

Replaces 23 callouts across 6 pages:
  - Dashboard Aperçu du jour: 3 callouts → kpi-dash-tasks-today / badge-week / trimester-t2
  - Dashboard Les 5 piliers: 5 callouts → kpi-dash-pilier-{slug}
  - Each pilier page Aperçu du pilier: 3 callouts → kpi-{slug}-achievements / habits / signature

Idempotent: skips columns that already contain an embed.

Usage:
    python scripts/convert_to_embeds.py --dry-run
    python scripts/convert_to_embeds.py --confirm
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
DEFAULT_BASE_URL = "https://citaman.github.io/life_os"


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} missing in env. Refusing to mutate Notion without explicit page configuration.")
    return value


TOKEN = require_env("NOTION_TOKEN")
client = Client(auth=TOKEN)

BASE_URL = (os.environ.get("LIFE_OS_BASE_URL") or os.environ.get("BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
DRY_RUN = False

P_DASH = require_env("PAGE_DASHBOARD")
P_INT = require_env("PAGE_INTERIEUR")
P_FAM = require_env("PAGE_FAMILLE")
P_PRO = require_env("PAGE_PRO_FI")
P_CRE = require_env("PAGE_CREATION")
P_SPI = require_env("PAGE_SPIRITUEL")

PAGE_TO_SLUG: dict[str, str] = {
    P_INT: "interieur",
    P_FAM: "famille",
    P_PRO: "pro-fi",
    P_CRE: "creation",
    P_SPI: "spirituel",
}

PAGE_NAMES = {
    P_DASH: "Dashboard",
    P_INT: "Intérieur",
    P_FAM: "Famille",
    P_PRO: "Pro & Financier",
    P_CRE: "Création",
    P_SPI: "Spirituel",
}

# Callout text → kpi slug (for pilier Aperçu)
APERCU_KEYS_TO_KPI = {
    "ACHIEVEMENTS ACTIFS": "{slug}-achievements",
    "HABITUDES ACTIVES": "{slug}-habits",
    # Signature metrics use various titles — match any "third" KPI callout
    "POIDS ACTUEL": "{slug}-signature",
    "DATE-NIGHT CETTE SEMAINE": "{slug}-signature",
    "NET WORTH": "{slug}-signature",
    "PROGRESSION TECH": "{slug}-signature",
    "PRÉDICATION AVRIL": "{slug}-signature",
}

# Dashboard Aperçu du jour callout text → kpi slug
DASHBOARD_APERCU = {
    "TÂCHES DU JOUR": "dash-tasks-today",
    "BADGE SEMAINE": "dash-badge-week",
    "TRIMESTRE T2 2026": "dash-trimester-t2",
}

# Dashboard Les 5 piliers heading_3 → kpi slug
DASHBOARD_PILIERS = {
    "Intérieur": "dash-pilier-interieur",
    "Famille": "dash-pilier-famille",
    "Pro & Financier": "dash-pilier-pro-fi",
    "Création": "dash-pilier-creation",
    "Spirituel": "dash-pilier-spirituel",
}


def block_text(b: dict[str, Any]) -> str:
    t = b["type"]
    body = b.get(t) or {}
    if isinstance(body, dict) and "rich_text" in body:
        return "".join(r.get("plain_text", "") for r in body["rich_text"])
    return ""


def list_children(block_id: str) -> list[dict[str, Any]]:
    out = []
    cursor = None
    while True:
        payload: dict[str, Any] = {"block_id": block_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        try:
            resp = client.blocks.children.list(**payload)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Could not read Notion children for block/page {block_id[:8]}...: {e}") from e
        out.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
    return out


def make_embed_block(url: str) -> dict[str, Any]:
    return {"object": "block", "type": "embed", "embed": {"url": url}}


def column_has_embed(column_id: str) -> bool:
    try:
        for c in list_children(column_id):
            if c["type"] == "embed":
                return True
    except Exception:
        pass
    return False


def replace_callout_with_embed(parent_id: str, callout_id: str, embed_slug: str) -> bool:
    """Insert embed after callout, then delete callout."""
    url = f"{BASE_URL}/kpi-{embed_slug}.html"
    if DRY_RUN:
        print(f"    DRY-RUN would insert {url} after callout {callout_id[:8]} then delete the callout")
        return True
    try:
        client.blocks.children.append(
            block_id=parent_id, after=callout_id, children=[make_embed_block(url)]
        )
        time.sleep(0.3)
        client.blocks.delete(block_id=callout_id)
        time.sleep(0.3)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"    ! swap failed {callout_id[:8]}: {e}")
        return False


# ---------- Dashboard ----------


def convert_dashboard(page_id: str) -> int:
    count = 0
    children = list_children(page_id)
    # Find Aperçu du jour column_list (first column_list on page)
    col_list_apercu = None
    for b in children:
        if b["type"] == "column_list":
            col_list_apercu = b
            break
    if not col_list_apercu:
        print(f"    ! Dashboard ({page_id[:8]}...) has no column_list for Aperçu du jour; skipped")
    else:
        columns = list_children(col_list_apercu["id"])
        for col in columns:
            if column_has_embed(col["id"]):
                continue
            col_children = list_children(col["id"])
            callout = next((c for c in col_children if c["type"] == "callout"), None)
            if not callout:
                continue
            text = block_text(callout)
            for key, slug in DASHBOARD_APERCU.items():
                if key in text:
                    if replace_callout_with_embed(col["id"], callout["id"], slug):
                        print(f"    · swapped '{key[:30]}' → kpi-{slug}")
                        count += 1
                    break

    # Find "Les 5 piliers" section — under H2 "Les 5 piliers", there are 2 column_lists
    children = list_children(page_id)  # refresh because we just mutated
    in_section = False
    found_pilier_section = False
    pilier_col_lists: list[dict[str, Any]] = []
    for b in children:
        if b["type"] == "heading_2":
            in_section = "Les 5 piliers" in block_text(b)
            found_pilier_section = found_pilier_section or in_section
            continue
        if in_section and b["type"] == "column_list":
            pilier_col_lists.append(b)

    if not found_pilier_section:
        print(f"    ! heading_2 'Les 5 piliers' not found on Dashboard ({page_id[:8]}...); pilier cards skipped")
    elif not pilier_col_lists:
        print(f"    ! Dashboard heading_2 'Les 5 piliers' found but no column_list was found below it")

    for col_list in pilier_col_lists:
        columns = list_children(col_list["id"])
        for col in columns:
            if column_has_embed(col["id"]):
                continue
            col_children = list_children(col["id"])
            callout = next((c for c in col_children if c["type"] == "callout"), None)
            if not callout:
                continue
            # Find heading_3 child inside the callout
            callout_children = list_children(callout["id"])
            heading_3 = next((c for c in callout_children if c["type"] == "heading_3"), None)
            if not heading_3:
                continue
            name = block_text(heading_3).strip()
            if name in DASHBOARD_PILIERS:
                slug = DASHBOARD_PILIERS[name]
                if replace_callout_with_embed(col["id"], callout["id"], slug):
                    print(f"    · swapped pilier card '{name}' → kpi-{slug}")
                    count += 1
    return count


# ---------- Per pilier Aperçu ----------


def convert_pilier(page_id: str, page_name: str) -> int:
    slug = PAGE_TO_SLUG[page_id]
    count = 0
    children = list_children(page_id)
    # First column_list = Aperçu du pilier
    col_list = None
    for b in children:
        if b["type"] == "column_list":
            col_list = b
            break
    if not col_list:
        print(f"    ! {page_name} ({page_id[:8]}...) has no column_list for Aperçu du pilier; skipped")
        return 0
    columns = list_children(col_list["id"])
    for col in columns:
        if column_has_embed(col["id"]):
            continue
        col_children = list_children(col["id"])
        callout = next((c for c in col_children if c["type"] == "callout"), None)
        if not callout:
            continue
        text = block_text(callout)
        for key, tmpl in APERCU_KEYS_TO_KPI.items():
            if key in text:
                kpi_slug = tmpl.format(slug=slug)
                if replace_callout_with_embed(col["id"], callout["id"], kpi_slug):
                    print(f"    · swapped '{key[:30]}' → kpi-{kpi_slug}")
                    count += 1
                break
    return count


# ---------- Main ----------


def main() -> None:
    global DRY_RUN
    parser = argparse.ArgumentParser(description="LEGACY: convert static Notion KPI callouts into live embeds.")
    parser.add_argument("--dry-run", action="store_true", help="Read Notion and print planned mutations without writing.")
    parser.add_argument("--confirm", action="store_true", help="Required for real mutations because this is a legacy one-shot script.")
    args = parser.parse_args()
    DRY_RUN = args.dry_run
    if not DRY_RUN and not args.confirm:
        sys.exit("ERROR: legacy mutation script requires --confirm. Run with --dry-run first to inspect planned swaps.")
    if DRY_RUN:
        print("DRY-RUN: no Notion mutations will be sent")
    else:
        print("CONFIRMED legacy migration: Notion mutations enabled")

    print("→ Dashboard")
    d = convert_dashboard(P_DASH)
    print(f"  total: {d} swaps")

    for page_id in [P_INT, P_FAM, P_PRO, P_CRE, P_SPI]:
        name = PAGE_NAMES[page_id]
        print(f"\n→ {name}")
        c = convert_pilier(page_id, name)
        print(f"  total: {c} swaps")


if __name__ == "__main__":
    main()
