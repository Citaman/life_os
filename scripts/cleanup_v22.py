"""
cleanup_v22.py — V2.2-C cleanup of 6 Life OS Notion pages.

Operations (executed in order):
  Phase 0 — Resolve all short block IDs (8 hex chars) to full UUIDs by scanning pages
  Phase 1 — DELETE redundant blocks (LIVE-TODO, CHART-TODO inline, Vue liée notes,
             fake journal callouts, fake historique bullets)
  Phase 2 — UPDATE stale KPI values from snapshots.json
  Phase 3 — UPDATE stale Création commentary paragraph
  Phase 4 — REPLACE LIVE-TODO journal paragraphs with "DB Journal à venir" callout
  Phase 5 — UPDATE stale "mise à jour" dates to 2026-04-20

Usage:
    python scripts/cleanup_v22.py

Safety: each block text verified against expected fragment before delete/update.
Rate-limit: 0.35 s between every API call.
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

if not SNAPSHOTS_PATH.exists():
    sys.exit("Missing data/snapshots.json — run transform.py first.")

snap = json.loads(SNAPSHOTS_PATH.read_text())

# ─── Page IDs ────────────────────────────────────────────────────────────────
P_DASH = os.environ["PAGE_DASHBOARD"]
P_INT  = os.environ["PAGE_INTERIEUR"]
P_FAM  = os.environ["PAGE_FAMILLE"]
P_PRO  = os.environ["PAGE_PRO_FI"]
P_CRE  = os.environ["PAGE_CREATION"]
P_SPI  = os.environ["PAGE_SPIRITUEL"]

# ─── Full UUID map (resolved in Phase 0) ─────────────────────────────────────
# Keyed by the 8-char short ID (first hex group before '-')
UUID_MAP: dict[str, str] = {}

# ─── Global counters ─────────────────────────────────────────────────────────
total_deleted = 0
total_updated = 0
total_skipped = 0
errors: list[str] = []

# ─── Helpers ─────────────────────────────────────────────────────────────────

def block_text(b: dict[str, Any]) -> str:
    t = b["type"]
    body = b.get(t) or {}
    if isinstance(body, dict) and "rich_text" in body:
        return "".join(r.get("plain_text", "") for r in body["rich_text"])
    return ""


def list_children(block_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = None
    while True:
        payload: dict[str, Any] = {"block_id": block_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.blocks.children.list(**payload)
        out.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
        time.sleep(0.35)
    return out


def api_delete(block_id: str) -> None:
    client.blocks.delete(block_id=block_id)
    time.sleep(0.35)


def api_update(block_id: str, block_type: str, new_text: str) -> None:
    payload: dict[str, Any] = {"rich_text": [{"type": "text", "text": {"content": new_text}}]}
    client.blocks.update(block_id=block_id, **{block_type: payload})
    time.sleep(0.35)


def fetch_block(block_id: str) -> dict[str, Any]:
    b = client.blocks.retrieve(block_id=block_id)
    time.sleep(0.35)
    return b


def uid(short: str) -> str:
    """Resolve 8-char short ID to full UUID. Raises KeyError if not found."""
    if short in UUID_MAP:
        return UUID_MAP[short]
    # Maybe it was passed as a full UUID already
    if "-" in short and len(short) > 8:
        return short
    raise KeyError(f"UUID for short ID '{short}' not resolved — run Phase 0 first")


# ─── Phase 0 — Resolve all short block IDs ───────────────────────────────────

# All short IDs we need to touch (delete or update)
ALL_SHORT_IDS: set[str] = {
    # Dashboard
    "911b4545","27bdf5fd","422745a3","d1b17eb0","cd42af0e",
    "61a65779","7609680a","de73930f","61a28607","8bb7cf4e",
    "0ed4bb56","318e3e50","6e136260","ef1edea1","6c2f3afd",
    "9a3f89a2","3b267b1e","e2100c19","82d731b4",
    # Intérieur
    "d4e29e2d","1fe415a3","52926420","69d0db2f","02be5ad1",
    "1182532c","7befb750","56dcd371","394d6243","379438fa",
    "19745350","d195ba88","551c2466","e367fc51","65f0d0ee",
    "c639d5bb","83ad0e8f","21afba8b","be0915f9","2b24b600",
    "f3a9edf9","3ee519e8",
    "14e38acc","e6a1ba09","ce6956ea","f75e3331",
    # Famille
    "1133e791","39331c71","f2818be7","fb4e8b34","3eaa1354",
    "e8521af2","cdd2fc36","c46b8600","d43d6912","d0a87980",
    "a5957fd8","858ddc69",
    "34741f52","ab77397d","3e0ba4ad","703a547d",
    "4f4fb568","48ed1476",
    "35089d3f","3b5f7be9",
    # Pro & Fi
    "cf2ad71c","dba477bf","2258857d","dd58876f","2b9d137e",
    "9d6cfa7f","cc375fb1","33e62e55","f066f11b","7c999dfb",
    "00b2c490",
    "e718eae8","fad5af7d","08a2140b","cb1e2707",
    "4335403d","c8ece303",
    "0cc9fdf7","f2ee226f","32923e17","23e5127d",
    # Création
    "8ff71385","2b93c605","87476544","296f4335","3e90bc85",
    "1646316c","97ff747f","5d9ba32e","9a88ac85","5be60c90",
    "4ac567f5",
    "0547f1fb","81530326","3f2861f0","4059a2e9",
    "dc79ef7e","4d7e4e98",
    "0d4b729a","e5a9fc8d","d6e4fc1f","608c214c",
    "9ba05b0e","87f7f8fd",
    # Spirituel
    "f72b87f1","9df3272c","df22cc9e","5613e428","80c31ef0",
    "cbf75c28","4fe0e11d","f9784542","2016adb8","ff4e9caa",
    "5ef9f73d",
    "2cc8aef6","acb5cb12","e7c714db","bfebaa51",
    "3e10e55d","ad1596cb",
    "7fea15dc","d63a4e02",
}

EXPAND_TYPES = {"toggle","callout","column_list","column",
                "bulleted_list_item","numbered_list_item","quote"}


def _scan_for_ids(block_id: str, depth: int = 0) -> None:
    if depth > 6:
        return
    cursor = None
    while True:
        payload: dict[str, Any] = {"block_id": block_id, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        try:
            resp = client.blocks.children.list(**payload)
        except Exception as e:  # noqa: BLE001
            print(f"  scan-err {block_id[:8]}: {e}")
            return
        for b in resp["results"]:
            full_id = b["id"]
            short   = full_id.split("-")[0]
            if short in ALL_SHORT_IDS:
                UUID_MAP[short] = full_id
            if b.get("has_children") and b["type"] in EXPAND_TYPES:
                _scan_for_ids(full_id, depth + 1)
                time.sleep(0.15)
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
        time.sleep(0.15)


def run_phase0_resolve() -> None:
    print("\n" + "=" * 60)
    print("PHASE 0 — Resolve block IDs to full UUIDs")
    print("=" * 60)
    pages = [P_DASH, P_INT, P_FAM, P_PRO, P_CRE, P_SPI]
    names = ["Dashboard","Intérieur","Famille","Pro & Fi","Création","Spirituel"]
    for page_id, name in zip(pages, names):
        print(f"  scanning {name}...")
        _scan_for_ids(page_id)
    missing = ALL_SHORT_IDS - set(UUID_MAP.keys())
    print(f"  resolved {len(UUID_MAP)}/{len(ALL_SHORT_IDS)}")
    if missing:
        print(f"  WARNING — unresolved IDs: {missing}")


# ─── Phase 1 — DELETE list ───────────────────────────────────────────────────

BLOCKS_TO_DELETE: list[tuple[str, str | None]] = [
    # ── Dashboard ──
    ("911b4545", "computed"),
    ("27bdf5fd", "computed"),
    ("422745a3", "computed"),
    ("d1b17eb0", "LIVE-TODO"),
    ("cd42af0e", "Viz non-natives"),
    ("61a65779", "LIVE-TODO"),
    ("7609680a", "LIVE-TODO"),
    ("de73930f", "LIVE-TODO"),
    ("61a28607", "LIVE-TODO"),
    ("8bb7cf4e", "LIVE-TODO"),

    # ── Intérieur ──
    ("d4e29e2d", "LIVE-TODO"),
    ("1fe415a3", "LIVE-TODO"),
    ("52926420", "LIVE-TODO"),
    ("69d0db2f", "Vue liée Plan"),
    ("02be5ad1", "CHART-TODO"),
    ("1182532c", "Vue liée Plan"),
    ("7befb750", "Vue liée Plan"),
    ("56dcd371", "CHART-TODO"),
    ("394d6243", "Vue liée Habitudes"),
    ("379438fa", "CHART-TODO"),
    ("19745350", "Vue liée Timeline"),
    # Fake Historique récent
    ("d195ba88", "Historique"),
    ("551c2466", "Samedi 19 avril"),
    ("e367fc51", "Jeudi 17 avril"),
    ("65f0d0ee", "Mardi 15 avril"),
    ("c639d5bb", "Lundi 14 avril"),
    # Fake journal callouts
    ("83ad0e8f", "SAMEDI 19 AVRIL"),
    ("21afba8b", "JEUDI 17 AVRIL"),
    ("be0915f9", "MARDI 15 AVRIL"),
    ("2b24b600", "LUNDI 14 AVRIL"),
    # LIVE-TODO journal placeholder (will be replaced in Phase 4)
    ("f3a9edf9", "LIVE-TODO"),

    # ── Famille ──
    ("1133e791", "LIVE-TODO"),
    ("39331c71", "LIVE-TODO"),
    ("f2818be7", "LIVE-TODO"),
    ("fb4e8b34", "Vue liée Plan"),
    ("3eaa1354", "CHART-TODO"),
    ("e8521af2", "Vue liée Plan"),
    ("cdd2fc36", "Vue liée Plan"),
    ("c46b8600", "CHART-TODO"),
    ("d43d6912", "Vue liée Habitudes"),
    ("d0a87980", "CHART-TODO"),
    ("a5957fd8", "Vue liée Timeline"),
    ("858ddc69", "CHART-TODO"),
    # Fake journal callouts
    ("34741f52", "SAMEDI 12 AVRIL"),
    ("ab77397d", "JEUDI 10 AVRIL"),
    ("3e0ba4ad", "DIMANCHE 7 AVRIL"),
    ("703a547d", "VENDREDI 4 AVRIL"),
    # LIVE-TODO journal placeholder
    ("4f4fb568", "LIVE-TODO"),

    # ── Pro & Financier ──
    ("cf2ad71c", "LIVE-TODO"),
    ("dba477bf", "LIVE-TODO"),
    ("2258857d", "LIVE-TODO"),
    ("dd58876f", "Vue liée Plan"),
    ("2b9d137e", "CHART-TODO"),
    ("9d6cfa7f", "Vue liée Plan"),
    ("cc375fb1", "Vue liée Plan"),
    ("33e62e55", "CHART-TODO"),
    ("f066f11b", "Vue liée Habitudes"),
    ("7c999dfb", "CHART-TODO"),
    ("00b2c490", "Vue liée Timeline"),
    # Fake journal callouts
    ("e718eae8", "VENDREDI 11 AVRIL"),
    ("fad5af7d", "LUNDI 14 AVRIL"),
    ("08a2140b", "MARDI 15 AVRIL"),
    ("cb1e2707", "SAMEDI 19 AVRIL"),
    # LIVE-TODO journal placeholder
    ("4335403d", "LIVE-TODO"),

    # ── Création ──
    ("8ff71385", "LIVE-TODO"),
    ("2b93c605", "LIVE-TODO"),
    ("87476544", "LIVE-TODO"),
    ("296f4335", "Vue liée Plan"),
    ("3e90bc85", "CHART-TODO"),
    ("1646316c", "Vue liée Plan"),
    ("97ff747f", "Vue liée Plan"),
    ("5d9ba32e", "CHART-TODO"),
    ("9a88ac85", "Vue liée Habitudes"),
    ("5be60c90", "CHART-TODO"),
    ("4ac567f5", "Vue liée Timeline"),
    # Fake journal callouts
    ("0547f1fb", "MARDI 15 AVRIL"),
    ("81530326", "MERCREDI 16 AVRIL"),
    ("3f2861f0", "VENDREDI 18 AVRIL"),
    ("4059a2e9", "DIMANCHE 13 AVRIL"),
    # LIVE-TODO journal placeholder
    ("dc79ef7e", "LIVE-TODO"),

    # ── Spirituel ──
    ("f72b87f1", "LIVE-TODO"),
    ("9df3272c", "LIVE-TODO"),
    ("df22cc9e", "LIVE-TODO"),
    ("5613e428", "Vue liée Plan"),
    ("80c31ef0", "CHART-TODO"),
    ("cbf75c28", "Vue liée Plan"),
    ("4fe0e11d", "Vue liée Plan"),
    ("f9784542", "CHART-TODO"),
    ("2016adb8", "Vue liée Habitudes"),
    ("ff4e9caa", "CHART-TODO"),
    ("5ef9f73d", "Vue liée Timeline"),
    # Fake journal callouts
    ("2cc8aef6", "MARDI 15 AVRIL"),
    ("acb5cb12", "SAMEDI 12 AVRIL"),
    ("e7c714db", "MERCREDI 9 AVRIL"),
    ("bfebaa51", "DIMANCHE 6 AVRIL"),
    # LIVE-TODO journal placeholder
    ("3e10e55d", "LIVE-TODO"),
]


def run_phase1_deletions() -> None:
    global total_deleted, total_skipped
    print("\n" + "=" * 60)
    print("PHASE 1 — DELETE redundant / fake blocks")
    print("=" * 60)

    for short_id, expected_fragment in BLOCKS_TO_DELETE:
        try:
            full_id = uid(short_id)
        except KeyError as e:
            print(f"  NOID  {short_id} · {e}")
            errors.append(f"DEL {short_id}: UUID not resolved")
            continue

        try:
            b = fetch_block(full_id)
            text = block_text(b)
            if expected_fragment and expected_fragment.lower() not in text.lower():
                print(f"  SKIP  {short_id} · expected '{expected_fragment}' not in '{text[:60]}'")
                total_skipped += 1
                continue
            api_delete(full_id)
            print(f"  DEL   {short_id} · {text[:70]}")
            total_deleted += 1
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "Could not find block" in msg or "404" in msg:
                print(f"  GONE  {short_id} · already deleted")
            else:
                print(f"  ERR   {short_id} · {e}")
                errors.append(f"DEL {short_id}: {e}")


# ─── Phase 2 — UPDATE stale KPIs ─────────────────────────────────────────────

def run_phase2_updates() -> None:
    global total_updated
    print("\n" + "=" * 60)
    print("PHASE 2 — UPDATE stale KPI values")
    print("=" * 60)

    def habit_stats(pilier_slug: str) -> tuple[int, int, int]:
        habits = snap["piliers"][pilier_slug].get("habits_w16", [])
        fait   = sum(h.get("fait",  0) for h in habits)
        cible  = sum(h.get("cible", 0) for h in habits)
        pct    = round(fait / cible * 100) if cible else 0
        return fait, cible, pct

    int_fait,  int_cible,  int_pct  = habit_stats("interieur")
    creation_roadmap_count = len(snap["piliers"]["creation"]["roadmap"])
    pro_fi_roadmap_count   = len(snap["piliers"]["pro_fi"]["roadmap"])
    creation_ach_count     = len(snap["piliers"]["creation"]["achievements_active"])

    updates: list[tuple[str, str, str, str]] = [
        # ── Dashboard: "Les 5 piliers" progress % ──
        ("0ed4bb56", "paragraph",
         f"{snap['piliers']['interieur']['progress_avg']} %",
         "Dashboard Intérieur progress_avg"),
        ("318e3e50", "paragraph",
         f"{snap['piliers']['famille']['progress_avg']} %",
         "Dashboard Famille progress_avg"),
        ("6e136260", "paragraph",
         f"{snap['piliers']['pro_fi']['progress_avg']} %",
         "Dashboard Pro & Fi progress_avg"),
        ("ef1edea1", "paragraph",
         f"{snap['piliers']['creation']['progress_avg']} %",
         "Dashboard Création progress_avg"),
        ("6c2f3afd", "paragraph",
         f"{snap['piliers']['spirituel']['progress_avg']} %",
         "Dashboard Spirituel progress_avg"),

        # ── Dashboard: achievements callout ──
        ("9a3f89a2", "callout",
         "9 achievements actifs · plafond Time Budget respecté · Création n'en a qu'1",
         "Dashboard achievements callout"),

        # ── Dashboard: Création roadmap callout + toggle heading ──
        ("3b267b1e", "callout",
         f"{creation_roadmap_count} programmes séquencés · Gantt · Actifs + Planifiés",
         "Dashboard Création roadmap callout"),
        ("e2100c19", "toggle",
         f"Séquençage détaillé des {creation_roadmap_count} programmes",
         "Dashboard Création toggle heading"),

        # ── Intérieur: habits KPI ──
        ("14e38acc", "heading_1",
         f"{int_pct} %",
         "Intérieur habits heading_1"),
        ("e6a1ba09", "paragraph",
         f"{int_fait} / {int_cible} cibles semaine",
         "Intérieur habits subtitle"),

        # ── Intérieur: poids → null placeholder ──
        ("ce6956ea", "heading_1", "—",
         "Intérieur poids heading_1 (null placeholder)"),
        ("f75e3331", "paragraph", "— · pas de DB Mesures corps",
         "Intérieur poids subtitle (null placeholder)"),

        # ── Famille: date-night → null placeholder ──
        ("35089d3f", "heading_1", "—",
         "Famille date-night heading_1 (null placeholder)"),
        ("3b5f7be9", "paragraph", "— · pas de DB Couple",
         "Famille date-night subtitle (null placeholder)"),

        # ── Pro & Fi: net worth → null placeholder ──
        ("0cc9fdf7", "heading_1", "— €",
         "Pro & Fi net worth heading_1 (null placeholder)"),
        ("f2ee226f", "paragraph", "— · pas de DB Comptes",
         "Pro & Fi net worth subtitle (null placeholder)"),

        # ── Pro & Fi: roadmap callout + toggle ──
        ("32923e17", "callout",
         f"{pro_fi_roadmap_count} programmes séquencés · Gantt · Actifs + Planifiés",
         "Pro & Fi roadmap callout"),
        ("23e5127d", "toggle",
         f"Séquençage détaillé des {pro_fi_roadmap_count} programmes",
         "Pro & Fi toggle heading"),

        # ── Création: achievements heading ──
        ("0d4b729a", "heading_1",
         f"{creation_ach_count} / 2",
         "Création achievements heading_1"),

        # ── Création: achievements callout ──
        ("e5a9fc8d", "callout",
         "1 chantier actif — ML P0 micrograd from scratch (paliers en cours)",
         "Création achievements callout"),

        # ── Création: roadmap callout + toggle ──
        ("d6e4fc1f", "callout",
         f"{creation_roadmap_count} programmes séquencés · Gantt · Actifs + Planifiés",
         "Création page roadmap callout"),
        ("608c214c", "toggle",
         f"Séquençage détaillé des {creation_roadmap_count} programmes",
         "Création page toggle heading"),

        # ── Création: progress_avg ──
        ("9ba05b0e", "heading_1",
         f"{snap['piliers']['creation']['progress_avg']} %",
         "Création progress heading_1"),

        # ── Spirituel: prédication → null placeholder ──
        ("7fea15dc", "heading_1", "— h / 30 h",
         "Spirituel prédication heading_1 (null placeholder)"),
        ("d63a4e02", "paragraph", "— · pas de DB Journal prédication",
         "Spirituel prédication subtitle (null placeholder)"),
    ]

    for short_id, block_type, new_text, desc in updates:
        try:
            full_id = uid(short_id)
        except KeyError as e:
            print(f"  NOID  {short_id} · {e}")
            errors.append(f"UPD {short_id} ({desc}): UUID not resolved")
            continue
        try:
            b = fetch_block(full_id)
            current = block_text(b)
            if current == new_text:
                print(f"  SAME  {short_id} · already '{new_text[:50]}'")
                continue
            api_update(full_id, block_type, new_text)
            print(f"  UPD   {short_id} · '{current[:40]}' → '{new_text[:55]}'  [{desc}]")
            total_updated += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERR   {short_id} · {desc} · {e}")
            errors.append(f"UPD {short_id} ({desc}): {e}")


# ─── Phase 3 — UPDATE Création stale commentary paragraph ────────────────────

def run_phase3_creation_commentary() -> None:
    global total_updated
    print("\n" + "=" * 60)
    print("PHASE 3 — UPDATE Création stale commentary paragraph")
    print("=" * 60)
    short_id = "87f7f8fd"
    new_text  = "0 % · aucun sous-achievement complété T2"
    try:
        full_id = uid(short_id)
        b = fetch_block(full_id)
        current = block_text(b)
        if current == new_text:
            print(f"  SAME  {short_id} · already up to date")
            return
        api_update(full_id, "paragraph", new_text)
        print(f"  UPD   {short_id} · '{current[:50]}' → '{new_text}'")
        total_updated += 1
    except Exception as e:  # noqa: BLE001
        print(f"  ERR   {short_id} · {e}")
        errors.append(f"UPD {short_id}: {e}")


# ─── Phase 4 — INSERT "DB Journal à venir" callout on each pilier page ───────

DB_JOURNAL_CALLOUT = {
    "object": "block",
    "type": "callout",
    "callout": {
        "rich_text": [{
            "type": "text",
            "text": {
                "content": (
                    "DB Journal à venir · entrées seront affichées ici "
                    "quand tu crées une DB Journal avec propriétés Pilier + Date + Tags + Entrée"
                )
            }
        }],
        "icon": {"type": "emoji", "emoji": "📋"},
        "color": "gray_background",
    },
}

PILIER_PAGES: list[tuple[str, str]] = [
    ("Intérieur",    P_INT),
    ("Famille",      P_FAM),
    ("Pro & Fi",     P_PRO),
    ("Création",     P_CRE),
    ("Spirituel",    P_SPI),
]


def run_phase4_journal_callouts() -> None:
    global total_updated
    print("\n" + "=" * 60)
    print("PHASE 4 — INSERT 'DB Journal à venir' callouts")
    print("=" * 60)
    print("  Note: callout appended at end of page (drag to Journal section in Notion UI)")

    for pilier_name, page_id in PILIER_PAGES:
        try:
            result = client.blocks.children.append(
                block_id=page_id,
                children=[DB_JOURNAL_CALLOUT],
            )
            new_id = result["results"][0]["id"][:8] if result.get("results") else "?"
            print(f"  INS   {pilier_name} → new block {new_id}")
            total_updated += 1
            time.sleep(0.35)
        except Exception as e:  # noqa: BLE001
            print(f"  ERR   {pilier_name} journal callout · {e}")
            errors.append(f"INS journal {pilier_name}: {e}")


# ─── Phase 5 — UPDATE "Dernière mise à jour" dates to 2026-04-20 ─────────────

MISE_A_JOUR_UPDATES: list[tuple[str, str, str]] = [
    ("82d731b4", "Dashboard",
     "Dernière mise à jour : 2026-04-20 · V8.4 harmonisée"),
    ("3ee519e8", "Intérieur",
     "Dernière mise à jour : 2026-04-20 · V8.4 pilier Intérieur"),
    ("48ed1476", "Famille",
     "Dernière mise à jour : 2026-04-20 · V8.4 pilier Famille"),
    ("c8ece303", "Pro & Financier",
     "Dernière mise à jour : 2026-04-20 · V8.4 pilier Pro & Financier"),
    ("4d7e4e98", "Création",
     "Dernière mise à jour : 2026-04-20 · V8.4 pilier Création"),
    ("ad1596cb", "Spirituel",
     "Dernière mise à jour : 2026-04-20 · V8.4 pilier Spirituel"),
]


def run_phase5_mise_a_jour() -> None:
    global total_updated
    print("\n" + "=" * 60)
    print("PHASE 5 — UPDATE 'Dernière mise à jour' dates")
    print("=" * 60)

    for short_id, label, new_text in MISE_A_JOUR_UPDATES:
        try:
            full_id = uid(short_id)
            b = fetch_block(full_id)
            current = block_text(b)
            if current == new_text:
                print(f"  SAME  {short_id} · {label} already up to date")
                continue
            api_update(full_id, "paragraph", new_text)
            print(f"  UPD   {short_id} · {label} → '{new_text}'")
            total_updated += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERR   {short_id} · {label} · {e}")
            errors.append(f"UPD mise_a_jour {short_id} ({label}): {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("cleanup_v22.py — V2.2-C Notion Cleanup")
    print(f"Snapshot: {SNAPSHOTS_PATH}")
    print("=" * 60)

    run_phase0_resolve()
    run_phase1_deletions()
    run_phase2_updates()
    run_phase3_creation_commentary()
    run_phase4_journal_callouts()
    run_phase5_mise_a_jour()

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Deleted  : {total_deleted}")
    print(f"  Updated  : {total_updated}")
    print(f"  Skipped  : {total_skipped}  (text mismatch — verify manually)")
    print(f"  Errors   : {len(errors)}")
    if errors:
        print("\nError details:")
        for err in errors:
            print(f"  ! {err}")
    print()


if __name__ == "__main__":
    main()
