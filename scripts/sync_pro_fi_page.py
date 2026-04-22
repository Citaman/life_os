"""
Refactor the Pro & Financier Notion page in place with canonical embed sections.

Goals:
- keep top intro + KPI columns untouched
- replace the mid-page raw DB sections with dynamic embeds
- keep the backstage toggle untouched
- idempotent enough for reruns

Usage:
    python scripts/sync_pro_fi_page.py
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

TOKEN = os.environ.get("NOTION_TOKEN")
if not TOKEN:
    sys.exit("ERROR: NOTION_TOKEN missing in env.")

client = Client(auth=TOKEN)

BASE_URL = "https://citaman.github.io/life_os"
PAGE_ID = os.environ.get("PAGE_PRO_FI", "348845e8-e836-81b0-aaf7-e3b81b92416c")
BACKSTAGE_LABEL = "Backstage · pilotage opérationnel"


def block_text(block: dict[str, Any]) -> str:
    t = block["type"]
    body = block.get(t) or {}
    if isinstance(body, dict) and "rich_text" in body:
        return "".join(r.get("plain_text", "") for r in body["rich_text"])
    if t == "child_database":
        return body.get("title", "")
    return ""


def list_children(block_id: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"block_id": block_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.blocks.children.list(**payload)
        blocks.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks


def make_divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def make_paragraph(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def make_heading_3(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def make_embed(url: str, caption: str | None = None) -> dict[str, Any]:
    embed: dict[str, Any] = {"url": url}
    if caption:
        embed["caption"] = [{"type": "text", "text": {"content": caption}}]
    return {"object": "block", "type": "embed", "embed": embed}


def insert_after(parent_id: str, after_block_id: str, children: list[dict[str, Any]]) -> None:
    client.blocks.children.append(block_id=parent_id, after=after_block_id, children=children)


def delete_block(block_id: str) -> None:
    client.blocks.delete(block_id=block_id)


def top_level_blocks() -> list[dict[str, Any]]:
    return list_children(PAGE_ID)


def find_backstage_toggle(blocks: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    for idx, block in enumerate(blocks):
        if block["type"] in {"toggle", "callout"} and BACKSTAGE_LABEL in block_text(block):
            return idx, block
    raise RuntimeError("Backstage toggle not found; aborting to avoid mutating end of page blindly.")


def find_section_range(blocks: list[dict[str, Any]], heading_text: str) -> tuple[int, int]:
    start = None
    for idx, block in enumerate(blocks):
        if block["type"] == "heading_2" and block_text(block) == heading_text:
            start = idx
            break
    if start is None:
        raise RuntimeError(f"Heading not found: {heading_text}")

    end = len(blocks)
    for idx in range(start + 1, len(blocks)):
        if blocks[idx]["type"] == "heading_2":
            end = idx
            break
        if blocks[idx]["type"] == "toggle" and BACKSTAGE_LABEL in block_text(blocks[idx]):
            end = idx
            break
    return start, end


def section_matches(blocks: list[dict[str, Any]], heading_text: str, expected_urls: list[str], expected_intro: str | None = None) -> bool:
    start, end = find_section_range(blocks, heading_text)
    urls = []
    intro = None
    for block in blocks[start + 1 : end]:
        if intro is None and block["type"] == "paragraph":
            intro = block_text(block).strip()
        if block["type"] == "embed":
            url = block.get("embed", {}).get("url")
            if url:
                urls.append(url)
    if expected_intro is not None and intro != expected_intro:
        return False
    return urls == expected_urls


def replace_section(heading_text: str, new_children: list[dict[str, Any]], expected_urls: list[str], expected_intro: str | None = None) -> bool:
    before = top_level_blocks()
    backstage_idx, backstage_block = find_backstage_toggle(before)
    start, end = find_section_range(before, heading_text)
    if start >= backstage_idx:
        raise RuntimeError(f"Refusing to mutate section beyond backstage boundary: {heading_text}")
    if section_matches(before, heading_text, expected_urls, expected_intro):
        print(f"  · {heading_text}: already up to date")
        return False

    old_slice = before[start:end]
    after_block_id = old_slice[-1]["id"]
    insert_after(PAGE_ID, after_block_id, new_children)
    time.sleep(0.6)

    refreshed = top_level_blocks()
    if not find_backstage_toggle(refreshed)[1]["id"] == backstage_block["id"]:
        raise RuntimeError("Backstage toggle changed unexpectedly after insertion.")

    new_start, new_end = find_section_range(refreshed, heading_text)
    if new_end <= new_start + 1:
        raise RuntimeError(f"Inserted section for {heading_text} looks empty.")

    for block in old_slice[1:]:
        delete_block(block["id"])
        time.sleep(0.25)

    print(f"  ✓ {heading_text}: replaced")
    return True


def cleanup_backstage_placeholder() -> bool:
    blocks = top_level_blocks()
    _, backstage = find_backstage_toggle(blocks)
    children = list_children(backstage["id"])
    for block in children:
        if "New database" in block_text(block):
            delete_block(block["id"])
            time.sleep(0.25)
            print("  ✓ Backstage: removed 'New database' placeholder")
            return True
    print("  · Backstage: no 'New database' placeholder found")
    return False


def embed_url(slug: str) -> str:
    return f"{BASE_URL}/{slug}.html"


SECTION_SPECS: list[dict[str, Any]] = [
    {
        "heading": "Achievements actifs",
        "intro": "Lecture V8 du pilier: objectifs structurants, paliers associés et tâches reliées de la semaine courante.",
        "expected_urls": [embed_url("achievements-pilier-pro-fi")],
        "children": [
            make_paragraph("Lecture V8 du pilier: objectifs structurants, paliers associés et tâches reliées de la semaine courante."),
            make_embed(embed_url("achievements-pilier-pro-fi"), "Achievements actifs · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Sous-achievements & paliers",
        "intro": "Jalons consolidés et critères mesurables du pilier, sans passer par la vue base brute.",
        "expected_urls": [embed_url("sous-achievements-pilier-pro-fi")],
        "children": [
            make_paragraph("Jalons consolidés et critères mesurables du pilier, sans passer par la vue base brute."),
            make_embed(embed_url("sous-achievements-pilier-pro-fi"), "Sous-achievements & paliers · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Tâches de la semaine",
        "intro": "Semaine courante: tâches datées restantes du pilier avec vue liste + répartition par jour.",
        "expected_urls": [embed_url("tasks-week-pilier-pro-fi")],
        "children": [
            make_paragraph("Semaine courante: tâches datées restantes du pilier avec vue liste + répartition par jour."),
            make_embed(embed_url("tasks-week-pilier-pro-fi"), "Tâches de la semaine · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Habitudes du pilier",
        "intro": "Régularité du pilier sur 4 semaines avec détail de la semaine active et fallback propre si la semaine courante est incomplète.",
        "expected_urls": [embed_url("heatmap-habits-pro-fi")],
        "children": [
            make_paragraph("Régularité du pilier sur 4 semaines avec détail de la semaine active et fallback propre si la semaine courante est incomplète."),
            make_embed(embed_url("heatmap-habits-pro-fi"), "Habitudes du pilier · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Évolution trimestre",
        "intro": "Progression hebdomadaire du pilier sur le trimestre utile, avec projection visible sans ouvrir le repo.",
        "expected_urls": [embed_url("area-pilier-pro-fi")],
        "children": [
            make_paragraph("Progression hebdomadaire du pilier sur le trimestre utile, avec projection visible sans ouvrir le repo."),
            make_embed(embed_url("area-pilier-pro-fi"), "Évolution trimestre · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Flux de temps pilier",
        "intro": "Lecture temps hebdomadaire du pilier Pro & Financier, branchée sur la baseline live du repo tant que le time tracker n'est pas encore connecté.",
        "expected_urls": [embed_url("sankey-pilier-pro-fi")],
        "children": [
            make_paragraph("Lecture temps hebdomadaire du pilier Pro & Financier, branchée sur la baseline live du repo tant que le time tracker n'est pas encore connecté."),
            make_embed(embed_url("sankey-pilier-pro-fi"), "Flux de temps pilier · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Dépendances — Graphe",
        "intro": "Arbre de dépendances stable entre achievements, sous-achievements et tâches du pilier.",
        "expected_urls": [embed_url("tree-deps-pro-fi")],
        "children": [
            make_paragraph("Arbre de dépendances stable entre achievements, sous-achievements et tâches du pilier."),
            make_embed(embed_url("tree-deps-pro-fi"), "Dépendances · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Sankey revenu + Treemap dépenses",
        "intro": "Lecture budgétaire du mois actif: répartition du revenu foyer, puis poids relatif des postes budgétés. Les dépenses réelles par compte restent sur la page dédiée transactions.",
        "expected_urls": [embed_url("sankey-revenu-profi"), embed_url("treemap-depenses-profi")],
        "children": [
            make_paragraph("Lecture budgétaire du mois actif: répartition du revenu foyer, puis poids relatif des postes budgétés. Les dépenses réelles par compte restent sur la page dédiée transactions."),
            make_embed(embed_url("sankey-revenu-profi"), "Sankey revenu · Pro & Financier"),
            make_heading_3("Treemap dépenses budgétées"),
            make_embed(embed_url("treemap-depenses-profi"), "Treemap dépenses budgétées · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Roadmap Pro & Financier 2026–2027",
        "intro": "Roadmap séquencée du pilier avec marqueur Aujourd'hui, sans retomber sur une simple timeline Notion brute.",
        "expected_urls": [embed_url("gantt-pilier-pro-fi")],
        "children": [
            make_paragraph("Roadmap séquencée du pilier avec marqueur Aujourd'hui, sans retomber sur une simple timeline Notion brute."),
            make_embed(embed_url("gantt-pilier-pro-fi"), "Roadmap · Pro & Financier"),
            make_divider(),
        ],
    },
    {
        "heading": "Journal du pilier",
        "intro": "Entrées récentes du journal rendues en timeline lisible, pendant que la base source reste dans le backstage.",
        "expected_urls": [embed_url("journal-pilier-pro-fi")],
        "children": [
            make_paragraph("Entrées récentes du journal rendues en timeline lisible, pendant que la base source reste dans le backstage."),
            make_embed(embed_url("journal-pilier-pro-fi"), "Journal · Pro & Financier"),
            make_divider(),
        ],
    },
]


def main() -> None:
    blocks = top_level_blocks()
    find_backstage_toggle(blocks)
    print("→ Sync Pro & Financier")
    changed = 0
    for spec in SECTION_SPECS:
        changed += int(replace_section(spec["heading"], spec["children"], spec["expected_urls"], spec.get("intro")))
    changed += int(cleanup_backstage_placeholder())
    print(f"\nDone. {changed} section(s) changed.")


if __name__ == "__main__":
    main()
