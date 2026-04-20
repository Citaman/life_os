"""
Transform raw_notion.json into snapshots.json with pre-computed metrics.

The snapshots.json is the canonical data consumed by V2 templates (and later V3 React app).

Usage:
    python scripts/transform.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = REPO_ROOT / "data" / "raw_notion.json"
OUT_PATH = REPO_ROOT / "data" / "snapshots.json"

CURRENT_WEEK = os.environ.get("CURRENT_WEEK", "W16")
CURRENT_TRIMESTER = os.environ.get("CURRENT_TRIMESTER", "T2 2026")
CURRENT_DATE = os.environ.get("CURRENT_DATE", "2026-04-19")

PILIERS = [
    {"slug": "interieur", "name": "Intérieur", "color_key": "green", "accent": "#2F7D5B", "tint_mid": "#7FB09A", "tint_light": "#D4E5DB"},
    {"slug": "famille", "name": "Famille", "color_key": "red", "accent": "#C84B4B", "tint_mid": "#E08B8B", "tint_light": "#F2D0D0"},
    {"slug": "pro_fi", "name": "Pro & Financier", "color_key": "blue", "accent": "#1E4D8C", "tint_mid": "#6A92C2", "tint_light": "#C9D8E8"},
    {"slug": "creation", "name": "Création", "color_key": "purple", "accent": "#6B3FA0", "tint_mid": "#A584CA", "tint_light": "#DDCEE7"},
    {"slug": "spirituel", "name": "Spirituel", "color_key": "yellow", "accent": "#B8860B", "tint_mid": "#D8B052", "tint_light": "#ECD9A8"},
]

# Targets for radar (actuel vs cible)
RADAR_TARGETS = {
    "Intérieur": {"cible": 85},
    "Famille": {"cible": 90},
    "Pro & Financier": {"cible": 80},
    "Création": {"cible": 80},
    "Spirituel": {"cible": 85},
}

# Weekly habit completion (12 semaines W05-W16) — historique, LIVE-TODO Phase B+
# Hardcoded en V2.0 · dérivé de user observations · à remplacer par DB Snapshots weekly
HISTORIC_WEEKLY_COMPLETION = {
    "Intérieur": [45, 52, 60, 68, 72, 75, 78, 80, 82, 85, 82, 82],
    "Famille":   [65, 68, 70, 72, 75, 78, 80, 82, 85, 85, 88, 90],
    "Pro & Financier": [50, 55, 60, 62, 65, 70, 72, 75, 78, 80, 82, 78],
    "Création":  [30, 35, 42, 48, 52, 55, 58, 60, 65, 68, 70, 72],
    "Spirituel": [70, 75, 75, 78, 80, 82, 85, 85, 88, 88, 90, 82],
}

# Time allocation per week (168h) — hardcoded V2 · Phase C DB Time Tracker
TIME_ALLOCATION = {
    "total": 168,
    "buckets": [
        {"cat": "Sommeil", "hours": 56, "subs": []},
        {"cat": "AVIV Travail", "hours": 42, "subs": [
            {"name": "Data work", "hours": 30},
            {"name": "Meetings", "hours": 8},
            {"name": "Admin", "hours": 4},
        ]},
        {"cat": "Admin / autre", "hours": 23, "subs": []},
        {"cat": "Famille", "hours": 22, "subs": [
            {"name": "Couple", "hours": 6},
            {"name": "Lecture James", "hours": 5},
            {"name": "Jeux enfants", "hours": 7},
            {"name": "Cuisine", "hours": 4},
        ]},
        {"cat": "Spirituel", "hours": 10, "subs": [
            {"name": "Réunions", "hours": 3},
            {"name": "Prédication", "hours": 3},
            {"name": "Étude perso", "hours": 2},
            {"name": "Étude Jillian", "hours": 2},
        ]},
        {"cat": "Intérieur", "hours": 8, "subs": [
            {"name": "Sport", "hours": 5},
            {"name": "Récup", "hours": 3},
        ]},
        {"cat": "Création", "hours": 7, "subs": [
            {"name": "Maths S1", "hours": 3},
            {"name": "Micrograd", "hours": 4},
        ]},
    ],
}


def parse_percent(text: str | None) -> int | None:
    """Extract a percent value from a Progression actuelle text field."""
    if not text:
        return None
    import re

    m = re.search(r"(\d+)\s*%", text)
    if m:
        return int(m.group(1))
    return None


def compute_pilier_progress(plan_pages: list[dict[str, Any]], pilier_name: str) -> int:
    """Average progression of En cours achievements for a pilier."""
    values: list[int] = []
    for p in plan_pages:
        if p.get("Type") != "Achievement":
            continue
        if p.get("Pilier") != pilier_name:
            continue
        if p.get("Statut") != "En cours":
            continue
        pct = parse_percent(p.get("Progression actuelle"))
        if pct is not None:
            values.append(pct)
    if not values:
        return 0
    return round(sum(values) / len(values))


def count_by_filter(pages: list[dict[str, Any]], **filters: Any) -> int:
    def match(p: dict[str, Any]) -> bool:
        return all(p.get(k) == v for k, v in filters.items())

    return sum(1 for p in pages if match(p))


def list_by_filter(pages: list[dict[str, Any]], **filters: Any) -> list[dict[str, Any]]:
    def match(p: dict[str, Any]) -> bool:
        for k, v in filters.items():
            pv = p.get(k)
            if k == "date_equals":
                # Expected form: ("date:Date prévue début", "2026-04-19")
                continue
            if pv != v:
                return False
        return True

    return [p for p in pages if match(p)]


def achievements_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    out = []
    for p in plan:
        if p.get("Type") == "Achievement" and p.get("Pilier") == pilier_name and p.get("Statut") == "En cours":
            out.append(
                {
                    "id": p["id"],
                    "url": p["url"],
                    "name": p.get("Nom"),
                    "progress": parse_percent(p.get("Progression actuelle")),
                    "critere": p.get("Critère de réussite"),
                    "cible_unite": p.get("Unité + Cible"),
                    "deadline": (p.get("Deadline") or {}).get("start"),
                    "start": (p.get("Date prévue début") or {}).get("start"),
                }
            )
    return sorted(out, key=lambda a: a.get("start") or "")


def sous_achievements_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    out = []
    for p in plan:
        if p.get("Type") == "Sous-achievement" and p.get("Pilier") == pilier_name:
            out.append(
                {
                    "id": p["id"],
                    "name": p.get("Nom"),
                    "parent": (p.get("Parent") or [None])[0] if p.get("Parent") else None,
                    "critere": p.get("Critère de réussite"),
                    "progress": parse_percent(p.get("Progression actuelle")),
                    "statut": p.get("Statut"),
                    "deadline": (p.get("Deadline") or {}).get("start"),
                }
            )
    return out


def roadmap_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    """All achievements (active + future) ordered by start date."""
    out = []
    for p in plan:
        if p.get("Type") == "Achievement" and p.get("Pilier") == pilier_name:
            out.append(
                {
                    "name": p.get("Nom"),
                    "start": (p.get("Date prévue début") or {}).get("start"),
                    "end": (p.get("Deadline") or {}).get("start"),
                    "active": p.get("Statut") == "En cours",
                    "progress": parse_percent(p.get("Progression actuelle")) or 0,
                }
            )
    return sorted(out, key=lambda a: a.get("start") or "2099")


def habits_of(hab_pages: list[dict[str, Any]], pilier_name: str, week: str) -> list[dict[str, Any]]:
    out = []
    for h in hab_pages:
        if h.get("Pilier") == pilier_name and h.get("Semaine") == week:
            days = [bool(h.get(d)) for d in ("Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim")]
            fait = int(h.get("Fait") or 0)
            cible = int(h.get("Cible /sem") or 0)
            out.append(
                {
                    "name": h.get("Nom"),
                    "cible": cible,
                    "days": days,
                    "fait": fait,
                    "score_pct": round(fait / cible * 100) if cible else 0,
                }
            )
    return out


def signature_metric(pilier_slug: str, plan: list[dict[str, Any]]) -> dict[str, Any]:
    """Pilier-specific hero KPI #3."""
    if pilier_slug == "interieur":
        return {"label": "Poids actuel", "value": "122,7 kg", "sub": "125 → 122,7 · -2,3 kg"}
    if pilier_slug == "famille":
        return {"label": "Date-night cette semaine", "value": "Samedi 21 h", "sub": "cinéma + resto quartier"}
    if pilier_slug == "pro_fi":
        return {"label": "Net worth", "value": "47 200 €", "sub": "+5 000 € vs W05"}
    if pilier_slug == "creation":
        return {"label": "Progression tech", "value": "27,5 %", "sub": "pilier le plus bas · à intensifier fin T2"}
    if pilier_slug == "spirituel":
        return {"label": "Prédication avril", "value": "24 h / 30 h", "sub": "80 % objectif mensuel"}
    return {}


def main() -> None:
    if not RAW_PATH.exists():
        sys.exit(f"Missing {RAW_PATH} — run fetch_notion.py first.")
    raw = json.loads(RAW_PATH.read_text())
    plan = raw["plan_execution"]
    hab = raw["habitudes"]

    print(f"Loaded {len(plan)} plan pages + {len(hab)} habit pages + {len(raw['backlog_vie'])} backlog pages.")

    piliers_out: dict[str, dict[str, Any]] = {}
    for p in PILIERS:
        name = p["name"]
        active = achievements_of(plan, name)
        sous_achs = sous_achievements_of(plan, name)
        habits_week = habits_of(hab, name, CURRENT_WEEK)
        roadmap = roadmap_of(plan, name)
        progress_avg = compute_pilier_progress(plan, name)
        series = HISTORIC_WEEKLY_COMPLETION.get(name, [0] * 12)
        time_pilier = next((b for b in TIME_ALLOCATION["buckets"] if b["cat"] == name), {"cat": name, "hours": 0, "subs": []})
        piliers_out[p["slug"]] = {
            **p,
            "progress_avg": progress_avg,
            "radar": {"actuel": series[-1], "cible": RADAR_TARGETS[name]["cible"], "gap": RADAR_TARGETS[name]["cible"] - series[-1]},
            "achievements_active": active,
            "sous_achievements": sous_achs,
            "habits_w16": habits_week,
            "habit_completion_12w": series,
            "time_pilier": time_pilier,
            "roadmap": roadmap,
            "signature_metric": signature_metric(p["slug"], plan),
        }

    # Dashboard-level metrics
    total_plan = len(plan)
    achievements_en_cours = count_by_filter(plan, Type="Achievement", Statut="En cours")
    sous_en_cours = count_by_filter(plan, Type="Sous-achievement", Statut="En cours")

    # Today tasks
    today = CURRENT_DATE
    tasks_today = [
        p
        for p in plan
        if p.get("Type") == "Tâche atomique"
        and (p.get("Date prévue début") or {}).get("start", "").startswith(today)
    ]
    tasks_today_done = sum(1 for t in tasks_today if t.get("Statut") == "Complété")

    # Overall habit score W16 (weighted avg)
    all_habits_w16 = [h for h in hab if h.get("Semaine") == CURRENT_WEEK]
    total_cible = sum(int(h.get("Cible /sem") or 0) for h in all_habits_w16)
    total_fait = sum(int(h.get("Fait") or 0) for h in all_habits_w16)
    badge_pct = round(total_fait / total_cible * 100) if total_cible else 0
    badge_status = "VERT" if badge_pct >= 80 else ("JAUNE" if badge_pct >= 50 else "ROUGE")

    snapshots = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "current_week": CURRENT_WEEK,
        "current_trimester": CURRENT_TRIMESTER,
        "current_date": CURRENT_DATE,
        "today_fr": "vendredi 19 avril 2026",
        "badge_week": {
            "status": badge_status,
            "score": badge_pct,
            "total_fait": total_fait,
            "total_cible": total_cible,
            "streak_weeks_vert": 3,  # TODO: compute from history
        },
        "tasks_today": {
            "done": tasks_today_done,
            "total": len(tasks_today),
            "items": [
                {
                    "name": t.get("Nom"),
                    "pilier": t.get("Pilier"),
                    "status": t.get("Statut"),
                }
                for t in tasks_today
            ],
        },
        "trimester_progress": {
            "achievements_total_active": achievements_en_cours,
            "sous_total_active": sous_en_cours,
            "total_plan_pages": total_plan,
        },
        "time_week": TIME_ALLOCATION,
        "historic_weekly_12w": {
            "weeks": [f"W{w:02d}" for w in range(5, 17)],
            "series": HISTORIC_WEEKLY_COMPLETION,
        },
        "piliers": piliers_out,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snapshots, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_PATH}")
    print(f"  · achievements actifs: {achievements_en_cours}")
    print(f"  · sous-achievements actifs: {sous_en_cours}")
    print(f"  · total Plan d'exécution pages: {total_plan}")
    print(f"  · tâches aujourd'hui: {tasks_today_done}/{len(tasks_today)}")
    print(f"  · badge W16: {badge_status} {badge_pct}%")


if __name__ == "__main__":
    main()
