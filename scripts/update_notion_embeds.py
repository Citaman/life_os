"""
Append an "Embeds live" section at the bottom of each Notion Life OS page
with iframe embed blocks pointing to https://citaman.github.io/life_os/*.html

Usage:
    python scripts/update_notion_embeds.py --dry-run
    python scripts/update_notion_embeds.py
"""

from __future__ import annotations

import argparse
import os
import sys
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

# Page ID → list of (title, embed_slug) pairs
PAGE_EMBEDS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    # Dashboard racine
    require_env("PAGE_DASHBOARD"): (
        "Dashboard",
        [
            ("Radar 5 piliers — actuel vs cible", "radar"),
            ("Flux de temps semaine 168 h", "sankey-week"),
            ("Évolution T2 — W05 → W26 projection", "area-t2"),
            ("Tâches semaine active par pilier — stacked column", "stacked-w16"),
        ],
    ),
    # Intérieur
    require_env("PAGE_INTERIEUR"): (
        "Intérieur",
        [
            ("Heatmap habitudes — 4 sem × 7 j", "heatmap-habits-interieur"),
            ("Flux Sankey — Intérieur 8 h/sem", "sankey-pilier-interieur"),
            ("Tree dépendances — Achievement → Sous", "tree-deps-interieur"),
            ("Évolution corps — Poids + mensurations", "line-poids-interieur"),
        ],
    ),
    # Famille
    require_env("PAGE_FAMILLE"): (
        "Famille",
        [
            ("Heatmap habitudes", "heatmap-habits-famille"),
            ("Flux Sankey — Famille 22 h/sem", "sankey-pilier-famille"),
            ("Tree dépendances", "tree-deps-famille"),
            ("Arbre familial — membres", "tree-family-famille"),
        ],
    ),
    # Pro & Financier
    require_env("PAGE_PRO_FI"): (
        "Pro & Financier",
        [
            ("Heatmap habitudes", "heatmap-habits-pro-fi"),
            ("Flux Sankey — Pro & Fi 42 h/sem", "sankey-pilier-pro-fi"),
            ("Tree dépendances", "tree-deps-pro-fi"),
            ("Sankey revenu — répartition mensuelle", "sankey-revenu-profi"),
            ("Treemap dépenses mensuelles", "treemap-depenses-profi"),
        ],
    ),
    # Création
    require_env("PAGE_CREATION"): (
        "Création",
        [
            ("Heatmap habitudes", "heatmap-habits-creation"),
            ("Flux Sankey — Création 7 h/sem", "sankey-pilier-creation"),
            ("Tree dépendances", "tree-deps-creation"),
            ("Skill Tree — 3 tracks prérequis", "skill-tree-creation"),
        ],
    ),
    # Spirituel
    require_env("PAGE_SPIRITUEL"): (
        "Spirituel",
        [
            ("Heatmap habitudes", "heatmap-habits-spirituel"),
            ("Flux Sankey — Spirituel 10 h/sem", "sankey-pilier-spirituel"),
            ("Tree dépendances", "tree-deps-spirituel"),
            ("Progression Vivre pour toujours — 31 chap.", "book-progression-spirituel"),
            ("Tendance prédication — 6 derniers mois", "line-predication-spirituel"),
        ],
    ),
}


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


def make_paragraph(text: str, italic: bool = False, color: str = "default") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text},
                    "annotations": {"italic": italic, "color": color},
                }
            ]
        },
    }


def make_embed(url: str, caption: str | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {"object": "block", "type": "embed", "embed": {"url": url}}
    if caption:
        block["embed"]["caption"] = [{"type": "text", "text": {"content": caption}}]
    return block


def make_bookmark(url: str, caption: str | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {"object": "block", "type": "bookmark", "bookmark": {"url": url}}
    if caption:
        block["bookmark"]["caption"] = [{"type": "text", "text": {"content": caption}}]
    return block


def make_callout(text: str, emoji: str = "🔗", color: str = "gray_background") -> dict[str, Any]:
    # Note: emoji allowed here because Notion callouts use icons; we'll use default icon
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": None,
            "color": color,
            "rich_text": [{"type": "text", "text": {"content": text}}],
        },
    }


def append_embeds_to_page(page_id: str, page_name: str, embeds: list[tuple[str, str]]) -> None:
    children: list[dict[str, Any]] = [
        make_divider(),
        make_heading_2(f"Embeds live · {page_name}"),
        make_paragraph(
            "Régénérés chaque matin 5 h UTC depuis le repo GitHub citaman/life_os. Cliquer l'iframe pour agrandir, ou ouvrir l'URL directement.",
            italic=True,
            color="gray",
        ),
    ]
    for title, slug in embeds:
        url = f"{BASE_URL}/{slug}.html"
        children.append(make_heading_3(title))
        children.append(make_embed(url, caption=title))
    children.append(make_divider())
    children.append(
        make_paragraph(
            f"Source: github.com/Citaman/life_os · deploy auto · {BASE_URL}/",
            italic=True,
            color="gray",
        )
    )

    # API accepts up to 100 children per call
    print(f"  appending {len(children)} blocks to {page_name} ({page_id[:8]}...)")
    if DRY_RUN:
        print(f"  DRY-RUN would append embeds: {[slug for _, slug in embeds]}")
        return
    client.blocks.children.append(block_id=page_id, children=children)


def main() -> None:
    global DRY_RUN
    parser = argparse.ArgumentParser(description="Append legacy live embed sections to Notion pages.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned append operations without writing Notion.")
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    if DRY_RUN:
        print("DRY-RUN: no Notion mutations will be sent")

    for page_id, (name, embeds) in PAGE_EMBEDS.items():
        print(f"→ {name}")
        try:
            append_embeds_to_page(page_id, name, embeds)
            verb = "planned" if DRY_RUN else "added"
            print(f"  ✓ OK {len(embeds)} embeds {verb}")
        except Exception as e:
            print(f"  ✗ failed to append embeds to {name} ({page_id[:8]}...). Check page env/access: {e}")
            sys.exit(1)
    print("\nAll 6 Notion pages checked." if DRY_RUN else "\nAll 6 Notion pages updated.")


if __name__ == "__main__":
    main()
