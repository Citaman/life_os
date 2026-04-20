"""
V2.1-C · Sync Notion pages with real embeds + real KPIs.

Operations per page:
 1. Delete legacy "Embeds live · {name}" section at the bottom (from Pass 10).
 2. For each CHART-TODO toggle, insert the corresponding embed block AFTER it,
    then delete the toggle.
 3. On the Dashboard, replace the 3 KPI card values (hardcoded "3 / 7", "82 %", "38 %")
    with real computed values from snapshots.json.

Usage:
    python scripts/sync_notion_embeds.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
TOKEN = os.environ["NOTION_TOKEN"]
client = Client(auth=TOKEN)

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_PATH = REPO_ROOT / "data" / "snapshots.json"

BASE_URL = "https://citaman.github.io/life_os"

# Page IDs
P_DASH = os.environ["PAGE_DASHBOARD"]
P_INT = os.environ["PAGE_INTERIEUR"]
P_FAM = os.environ["PAGE_FAMILLE"]
P_PRO = os.environ["PAGE_PRO_FI"]
P_CRE = os.environ["PAGE_CREATION"]
P_SPI = os.environ["PAGE_SPIRITUEL"]

# Per-page: H2 section heading (substring match) → embed slug
PAGE_EMBEDS_INLINE: dict[str, dict[str, str]] = {
    P_DASH: {
        "Équilibre 5 piliers": "radar",
        "Flux de temps semaine": "sankey-week",
        "Aujourd'hui": "stacked-w16",
        "Progression T2": "area-t2",
    },
    P_INT: {
        "Flux de temps pilier": "sankey-pilier-interieur",
        "Dépendances": "tree-deps-interieur",
        "Habitudes du pilier": "heatmap-habits-interieur",
        "Évolution corps": "line-poids-interieur",
        "Évolution trimestre": "area-t2",  # shared dashboard embed
    },
    P_FAM: {
        "Flux de temps pilier": "sankey-pilier-famille",
        "Dépendances": "tree-deps-famille",
        "Habitudes du pilier": "heatmap-habits-famille",
        "Membres de la famille": "tree-family-famille",
        "Évolution trimestre": "area-t2",
    },
    P_PRO: {
        "Flux de temps pilier": "sankey-pilier-pro-fi",
        "Dépendances": "tree-deps-pro-fi",
        "Habitudes du pilier": "heatmap-habits-pro-fi",
        "Sankey revenu": "sankey-revenu-profi",
        "Treemap": "treemap-depenses-profi",
        "Évolution trimestre": "area-t2",
    },
    P_CRE: {
        "Flux de temps pilier": "sankey-pilier-creation",
        "Dépendances": "tree-deps-creation",
        "Habitudes du pilier": "heatmap-habits-creation",
        "Skill Tree": "skill-tree-creation",
        "Évolution trimestre": "area-t2",
    },
    P_SPI: {
        "Flux de temps pilier": "sankey-pilier-spirituel",
        "Dépendances": "tree-deps-spirituel",
        "Habitudes du pilier": "heatmap-habits-spirituel",
        "Progression livre": "book-progression-spirituel",
        "Tendance prédication": "line-predication-spirituel",
        "Évolution trimestre": "area-t2",
    },
}

PAGE_NAMES = {
    P_DASH: "Dashboard",
    P_INT: "Intérieur",
    P_FAM: "Famille",
    P_PRO: "Pro & Financier",
    P_CRE: "Création",
    P_SPI: "Spirituel",
}


def block_text(b: dict[str, Any]) -> str:
    t = b["type"]
    body = b.get(t) or {}
    if isinstance(body, dict) and "rich_text" in body:
        return "".join(r.get("plain_text", "") for r in body["rich_text"])
    return ""


def list_children(page_id: str) -> list[dict[str, Any]]:
    out = []
    cursor = None
    while True:
        payload: dict[str, Any] = {"block_id": page_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.blocks.children.list(**payload)
        out.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
    return out


def make_embed_block(url: str) -> dict[str, Any]:
    return {"object": "block", "type": "embed", "embed": {"url": url}}


def delete_block(block_id: str) -> None:
    client.blocks.delete(block_id=block_id)


def insert_after(parent_id: str, after_block_id: str, blocks: list[dict[str, Any]]) -> None:
    client.blocks.children.append(block_id=parent_id, after=after_block_id, children=blocks)


# ---------- Step 1: delete legacy "Embeds live · X" sections ----------


def delete_legacy_embed_section(page_id: str, page_name: str) -> int:
    """Find the last 'Embeds live · X' heading_2 on the page and delete everything
    from (and including) the divider just before it to the end of the page."""
    children = list_children(page_id)
    # Find the H2 "Embeds live · X"
    h2_idx = None
    for i, b in enumerate(children):
        if b["type"] == "heading_2" and "Embeds live" in block_text(b):
            h2_idx = i
            break
    if h2_idx is None:
        return 0
    # Back up one to catch the divider just before
    start = h2_idx
    if start > 0 and children[start - 1]["type"] == "divider":
        start = h2_idx - 1
    to_delete = children[start:]
    for b in to_delete:
        try:
            delete_block(b["id"])
        except Exception as e:  # noqa: BLE001
            print(f"    ! skip delete {b['id'][:8]}: {e}")
    return len(to_delete)


# ---------- Step 2: inline replace CHART-TODO toggles with embeds ----------


def inline_replace_chart_todos(page_id: str, page_name: str, mapping: dict[str, str]) -> int:
    """Walk the page blocks, track current H2 section, when a toggle whose text
    starts with 'CHART-TODO' is found, insert the mapped embed after it + delete it."""
    children = list_children(page_id)
    current_h2 = ""
    swap_plan: list[tuple[str, str]] = []  # (toggle_id, embed_slug)
    for b in children:
        if b["type"] == "heading_2":
            current_h2 = block_text(b)
            continue
        if b["type"] == "toggle":
            summary = block_text(b)
            if "CHART-TODO" not in summary:
                continue
            # Find matching section by keyword
            for section_key, slug in mapping.items():
                if section_key in current_h2:
                    swap_plan.append((b["id"], slug))
                    break
    print(f"  · identified {len(swap_plan)} CHART-TODO toggles to replace")
    count = 0
    for toggle_id, slug in swap_plan:
        url = f"{BASE_URL}/{slug}.html"
        try:
            insert_after(page_id, toggle_id, [make_embed_block(url)])
            delete_block(toggle_id)
            count += 1
            time.sleep(0.35)  # respect rate limits
        except Exception as e:  # noqa: BLE001
            print(f"    ! skip swap {toggle_id[:8]}: {e}")
    return count


# ---------- Step 3: update Dashboard KPI callouts with real values ----------


def _update_heading1_text(block_id: str, new_text: str) -> None:
    client.blocks.update(
        block_id=block_id,
        heading_1={"rich_text": [{"type": "text", "text": {"content": new_text}}]},
    )


def _update_paragraph_text(block_id: str, new_text: str, italic: bool = False, color: str = "default") -> None:
    client.blocks.update(
        block_id=block_id,
        paragraph={
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": new_text},
                    "annotations": {"italic": italic, "color": color},
                }
            ]
        },
    )


def update_dashboard_kpis(snapshots: dict[str, Any]) -> int:
    """Walk dashboard blocks, find the 3 KPI callouts in the Aperçu column_list,
    and update their heading + paragraphs with real values from snapshots."""
    children = list_children(P_DASH)
    # Find the first column_list (it's the Aperçu KPIs)
    column_list_id = None
    for b in children:
        if b["type"] == "column_list":
            column_list_id = b["id"]
            break
    if not column_list_id:
        print("  · no column_list found — aperçu KPIs not updated")
        return 0

    # Each column contains a callout with heading_1 + paragraphs
    columns = list_children(column_list_id)
    if len(columns) < 3:
        print(f"  · expected 3 columns, got {len(columns)}")
        return 0

    # Values from snapshots
    tasks_done = snapshots["tasks_today"]["done"]
    tasks_total = snapshots["tasks_today"]["total"]
    badge = snapshots["badge_week"]
    tri = snapshots["trimester_progress"]

    kpi_values = [
        {  # Column 1: TÂCHES DU JOUR
            "heading": f"{tasks_done} / {tasks_total}" if tasks_total else "0 / 0",
            "sub": f"complétées · {max(0, tasks_total - tasks_done)} en attente" if tasks_total else "aucune tâche datée aujourd'hui",
            "note": "computed · Plan d'exécution.Tâche atomique filter Date = today",
        },
        {  # Column 2: BADGE SEMAINE
            "heading": f"{badge['score']} %" if badge["score"] is not None else "—",
            "sub": f"{badge['status']} · {badge['total_fait']} / {badge['total_cible']} habitudes tenues" if badge["status"] else "aucune donnée habitude",
            "note": "computed · somme Habitudes.Fait / somme Cible /sem pour W16",
        },
        {  # Column 3: TRIMESTRE T2
            "heading": f"{tri['t2_percent']} %" if tri["t2_percent"] is not None else "—",
            "sub": f"{tri['sous_total_done']} sous-achievements done · {tri['sous_total_active']} en cours · {tri['total_plan_pages']} pages Plan d'exécution",
            "note": "computed · sous-achievements Atteint/Complété / (done+en cours)",
        },
    ]

    updated = 0
    for col, kpi in zip(columns, kpi_values):
        col_children = list_children(col["id"])
        # Look for the single callout
        callout = next((c for c in col_children if c["type"] == "callout"), None)
        if not callout:
            continue
        inner = list_children(callout["id"])
        h1 = next((b for b in inner if b["type"] == "heading_1"), None)
        paragraphs = [b for b in inner if b["type"] == "paragraph"]
        if h1:
            try:
                _update_heading1_text(h1["id"], kpi["heading"])
                updated += 1
            except Exception as e:  # noqa: BLE001
                print(f"    ! update h1 {h1['id'][:8]}: {e}")
        if len(paragraphs) >= 1:
            try:
                _update_paragraph_text(paragraphs[0]["id"], kpi["sub"])
            except Exception as e:  # noqa: BLE001
                print(f"    ! update sub {paragraphs[0]['id'][:8]}: {e}")
        if len(paragraphs) >= 2:
            try:
                _update_paragraph_text(paragraphs[1]["id"], kpi["note"], italic=True, color="gray")
            except Exception as e:  # noqa: BLE001
                print(f"    ! update note {paragraphs[1]['id'][:8]}: {e}")
        time.sleep(0.4)
    return updated


# ---------- Main ----------


def main() -> None:
    if not SNAPSHOTS_PATH.exists():
        sys.exit("Missing snapshots.json — run transform.py first.")
    snapshots = json.loads(SNAPSHOTS_PATH.read_text())

    total_deleted = 0
    total_swapped = 0

    for page_id, name in PAGE_NAMES.items():
        print(f"\n→ {name}")
        print(f"  [1/2] deleting legacy Embeds live · {name} section")
        deleted = delete_legacy_embed_section(page_id, name)
        print(f"    · {deleted} legacy blocks deleted")
        total_deleted += deleted

        print(f"  [2/2] inline-replace CHART-TODO toggles with embeds")
        mapping = PAGE_EMBEDS_INLINE.get(page_id, {})
        swapped = inline_replace_chart_todos(page_id, name, mapping)
        print(f"    · {swapped} toggles swapped for embeds")
        total_swapped += swapped

    # Dashboard KPIs: real values
    print(f"\n→ Dashboard KPIs with real values")
    updated = update_dashboard_kpis(snapshots)
    print(f"  · {updated} KPI callout headings updated")

    print(f"\nDone. legacy deleted: {total_deleted} · toggles swapped: {total_swapped} · KPI headings: {updated}")


if __name__ == "__main__":
    main()
