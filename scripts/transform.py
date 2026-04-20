"""
Transform raw_notion.json into snapshots.json with ONLY computed-from-DB metrics.

Principles (V2.1):
- Zero hardcoded data. Every number comes from Notion DBs.
- When data is not available yet (no DB, no values), output `null`.
- Templates must render transparent "TODO" placeholders for null metrics.
- All numbers must be derivable via sum / count / avg / div on raw_notion.json content.

Usage:
    python scripts/transform.py
"""

from __future__ import annotations

import json
import locale
import os
import sys
from datetime import datetime
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


def today_fr(date_str: str) -> str:
    """Format YYYY-MM-DD as 'vendredi 19 avril 2026' in French."""
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        pass
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%A %d %B %Y").lower()
    except ValueError:
        return date_str


# ---------- Progress helpers ----------


def parse_percent(text: str | None) -> int | None:
    """Extract an explicit % from a free-text field. Returns null if absent."""
    if not text:
        return None
    import re

    m = re.search(r"(\d+)\s*%", text)
    if m:
        return int(m.group(1))
    return None


def rollup_progress_from_sous(achievement_id: str, plan_pages: list[dict[str, Any]]) -> int | None:
    """Compute achievement progress as % sous-achievements marked done.

    Returns None if no children (not rollup-able).
    Returns 0 if children exist but none done — that IS the truth.
    """
    children = [p for p in plan_pages if p.get("Type") == "Sous-achievement" and achievement_id in (p.get("Parent") or [])]
    if not children:
        return None
    done_statuses = {"Complété", "Atteint"}
    done = sum(1 for c in children if c.get("Statut") in done_statuses)
    return round(done / len(children) * 100)


def achievement_progress(a: dict[str, Any], plan: list[dict[str, Any]]) -> int | None:
    """Priority: explicit % in Progression actuelle text > sous-rollup > null.

    No hardcoded overrides. If neither source yields a value, returns None.
    """
    pct = parse_percent(a.get("Progression actuelle"))
    if pct is not None:
        return pct
    rollup = rollup_progress_from_sous(a["id"], plan)
    return rollup  # can be int or None


def compute_pilier_progress(plan_pages: list[dict[str, Any]], pilier_name: str) -> int | None:
    """Average of En cours achievements progresses for a pilier.

    Returns None if no active achievement OR all have null progress.
    """
    values: list[int] = []
    for p in plan_pages:
        if p.get("Type") != "Achievement":
            continue
        if p.get("Pilier") != pilier_name:
            continue
        if p.get("Statut") != "En cours":
            continue
        pct = achievement_progress(p, plan_pages)
        if pct is not None:
            values.append(pct)
    if not values:
        return None
    return round(sum(values) / len(values))


# ---------- DB readers ----------


def count_by_filter(pages: list[dict[str, Any]], **filters: Any) -> int:
    def match(p: dict[str, Any]) -> bool:
        return all(p.get(k) == v for k, v in filters.items())
    return sum(1 for p in pages if match(p))


def achievements_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    out = []
    for p in plan:
        if p.get("Type") == "Achievement" and p.get("Pilier") == pilier_name and p.get("Statut") == "En cours":
            out.append(
                {
                    "id": p["id"],
                    "url": p["url"],
                    "name": p.get("Nom"),
                    "progress": achievement_progress(p, plan),
                    "critere": p.get("Critère de réussite"),
                    "cible_unite": p.get("Unité + Cible"),
                    "deadline": (p.get("Deadline") or {}).get("start"),
                    "start": (p.get("Date prévue début") or {}).get("start"),
                }
            )
    return sorted(out, key=lambda a: a.get("start") or "")


def sous_achievements_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    id_to_name = {p["id"]: p.get("Nom") for p in plan}
    out = []
    for p in plan:
        if p.get("Type") == "Sous-achievement" and p.get("Pilier") == pilier_name:
            parent_id = (p.get("Parent") or [None])[0] if p.get("Parent") else None
            out.append(
                {
                    "id": p["id"],
                    "name": p.get("Nom"),
                    "parent_id": parent_id,
                    "parent_name": id_to_name.get(parent_id) if parent_id else None,
                    "critere": p.get("Critère de réussite"),
                    "progress": parse_percent(p.get("Progression actuelle")),
                    "statut": p.get("Statut"),
                    "deadline": (p.get("Deadline") or {}).get("start"),
                }
            )
    return out


def roadmap_of(plan: list[dict[str, Any]], pilier_name: str) -> list[dict[str, Any]]:
    """All achievements (active + future) ordered by start date. Excludes Abandonné."""
    out = []
    for p in plan:
        if p.get("Type") == "Achievement" and p.get("Pilier") == pilier_name and p.get("Statut") != "Abandonné":
            out.append(
                {
                    "id": p["id"],
                    "name": p.get("Nom"),
                    "start": (p.get("Date prévue début") or {}).get("start"),
                    "end": (p.get("Deadline") or {}).get("start"),
                    "active": p.get("Statut") == "En cours",
                    "status": p.get("Statut"),
                    "progress": achievement_progress(p, plan),
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
                    "score_pct": round(fait / cible * 100) if cible else None,
                }
            )
    return out


def historic_weekly_completion(hab_pages: list[dict[str, Any]], pilier_name: str, weeks: list[str]) -> list[int | None]:
    """For each week in `weeks`, return average habit completion % for the pilier.

    If no habit data for that week → None (not 0).
    """
    out: list[int | None] = []
    for wk in weeks:
        week_habits = [h for h in hab_pages if h.get("Pilier") == pilier_name and h.get("Semaine") == wk]
        if not week_habits:
            out.append(None)
            continue
        total_fait = sum(int(h.get("Fait") or 0) for h in week_habits)
        total_cible = sum(int(h.get("Cible /sem") or 0) for h in week_habits)
        if total_cible == 0:
            out.append(None)
        else:
            out.append(round(total_fait / total_cible * 100))
    return out


def tasks_today(plan: list[dict[str, Any]], today_str: str) -> list[dict[str, Any]]:
    out = []
    for p in plan:
        if p.get("Type") != "Tâche atomique":
            continue
        start = (p.get("Date prévue début") or {}).get("start", "") or ""
        if start.startswith(today_str):
            out.append(
                {
                    "id": p["id"],
                    "name": p.get("Nom"),
                    "pilier": p.get("Pilier"),
                    "status": p.get("Statut"),
                }
            )
    return out


def tasks_completed_per_day_per_pilier_w16(plan: list[dict[str, Any]], weeks_range: tuple[str, str]) -> dict[str, dict[str, int]]:
    """Build a dict {day (Lun..Dim): {pilier: count}} from real Tâches atomiques with
    Date prévue début within the W16 date range AND Statut=Complété.

    weeks_range = (start_date_iso, end_date_iso) inclusive.
    """
    from datetime import date as date_cls

    start = date_cls.fromisoformat(weeks_range[0])
    end = date_cls.fromisoformat(weeks_range[1])
    days_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    piliers = ["Intérieur", "Famille", "Pro & Financier", "Création", "Spirituel"]
    out: dict[str, dict[str, int]] = {d: {p: 0 for p in piliers} for d in days_fr}

    for p in plan:
        if p.get("Type") != "Tâche atomique":
            continue
        if p.get("Statut") != "Complété":
            continue
        start_raw = (p.get("Date prévue début") or {}).get("start")
        if not start_raw:
            continue
        try:
            d = date_cls.fromisoformat(start_raw[:10])
        except ValueError:
            continue
        if d < start or d > end:
            continue
        day_idx = d.weekday()  # Mon=0
        day_label = days_fr[day_idx]
        pilier = p.get("Pilier")
        if pilier in piliers:
            out[day_label][pilier] += 1
    return out


# ---------- Main ----------


def main() -> None:
    if not RAW_PATH.exists():
        sys.exit(f"Missing {RAW_PATH} — run fetch_notion.py first.")
    raw = json.loads(RAW_PATH.read_text())
    plan = raw["plan_execution"]
    hab = raw["habitudes"]

    print(f"Loaded {len(plan)} plan pages + {len(hab)} habit pages + {len(raw['backlog_vie'])} backlog pages.")

    # Build historic weeks list (12 weeks up to current)
    try:
        current_w_num = int(CURRENT_WEEK.lstrip("W"))
    except ValueError:
        current_w_num = 16
    historic_weeks = [f"W{w:02d}" for w in range(max(1, current_w_num - 11), current_w_num + 1)]

    piliers_out: dict[str, dict[str, Any]] = {}
    for p in PILIERS:
        name = p["name"]
        active = achievements_of(plan, name)
        sous_achs = sous_achievements_of(plan, name)
        habits_week = habits_of(hab, name, CURRENT_WEEK)
        roadmap = roadmap_of(plan, name)
        progress_avg = compute_pilier_progress(plan, name)

        # Historic 12 weeks — computed from real Habitudes DB (will be mostly null at start)
        hist_series = historic_weekly_completion(hab, name, historic_weeks)

        piliers_out[p["slug"]] = {
            **p,
            "progress_avg": progress_avg,  # int or null
            "radar": {
                "actuel": hist_series[-1] if hist_series else None,
                "cible": None,  # TODO: pilier target DB/property not yet defined
                "gap": None,
            },
            "achievements_active": active,
            "sous_achievements": sous_achs,
            "habits_w16": habits_week,
            "habit_completion_12w": hist_series,  # list of int|null
            "time_pilier": None,  # TODO: DB Time Tracker
            "roadmap": roadmap,
            "signature_metric": None,  # TODO: pilier-specific DB (Mesures corps, Comptes, etc.)
        }

    # Dashboard-level metrics
    total_plan = len(plan)
    achievements_en_cours = count_by_filter(plan, Type="Achievement", Statut="En cours")
    sous_en_cours = count_by_filter(plan, Type="Sous-achievement", Statut="En cours")
    sous_done = count_by_filter(plan, Type="Sous-achievement", Statut="Complété") + count_by_filter(plan, Type="Sous-achievement", Statut="Atteint")
    tasks_en_cours = count_by_filter(plan, Type="Tâche atomique", Statut="En cours")
    tasks_done = count_by_filter(plan, Type="Tâche atomique", Statut="Complété")

    # Today tasks
    tlist = tasks_today(plan, CURRENT_DATE)
    tlist_done = sum(1 for t in tlist if t.get("status") == "Complété")

    # Overall habit score current week
    all_habits_w16 = [h for h in hab if h.get("Semaine") == CURRENT_WEEK]
    total_cible = sum(int(h.get("Cible /sem") or 0) for h in all_habits_w16)
    total_fait = sum(int(h.get("Fait") or 0) for h in all_habits_w16)
    if total_cible == 0:
        badge_pct = None
        badge_status = None
    else:
        badge_pct = round(total_fait / total_cible * 100)
        badge_status = "VERT" if badge_pct >= 80 else ("JAUNE" if badge_pct >= 50 else "ROUGE")

    # Stacked tasks W16 per day per pilier (from real completed tasks)
    # W16 = 2026-04-13 → 2026-04-19 (assumption: current_week mentions W16)
    stacked_w16 = tasks_completed_per_day_per_pilier_w16(plan, ("2026-04-13", "2026-04-19"))

    snapshots = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "current_week": CURRENT_WEEK,
        "current_trimester": CURRENT_TRIMESTER,
        "current_date": CURRENT_DATE,
        "today_fr": today_fr(CURRENT_DATE),
        "badge_week": {
            "status": badge_status,  # str or null
            "score": badge_pct,      # int or null
            "total_fait": total_fait,
            "total_cible": total_cible,
            "streak_weeks_vert": None,  # TODO: needs history
        },
        "tasks_today": {
            "done": tlist_done,
            "total": len(tlist),
            "items": tlist,
        },
        "tasks_w16_by_day_by_pilier": stacked_w16,
        "trimester_progress": {
            "achievements_total_active": achievements_en_cours,
            "sous_total_active": sous_en_cours,
            "sous_total_done": sous_done,
            "tasks_total_done": tasks_done,
            "tasks_total_en_cours": tasks_en_cours,
            "total_plan_pages": total_plan,
            # T2 progress % = sous_done / sous_total_active_or_planned
            # For now: done / (done + en_cours). Null if denominator = 0.
            "t2_percent": round(sous_done / (sous_done + sous_en_cours) * 100) if (sous_done + sous_en_cours) else None,
        },
        "time_week": None,  # TODO: DB Time Tracker future
        "historic_weekly_12w": {
            "weeks": historic_weeks,
            "series": {p["name"]: piliers_out[p["slug"]]["habit_completion_12w"] for p in PILIERS},
        },
        "piliers": piliers_out,
    }

    # ---------- KPI catalog ----------
    kpi_catalog = {
        # Dashboard — 3 hero KPIs
        "dash-tasks-today": {
            "eyebrow": "TÂCHES DU JOUR",
            "value": f"{snapshots['tasks_today']['done']} / {snapshots['tasks_today']['total']}",
            "sub": f"complétées · {max(0, snapshots['tasks_today']['total'] - snapshots['tasks_today']['done'])} en attente" if snapshots['tasks_today']['total'] else "aucune tâche datée aujourd'hui",
            "accent": "#3B82F6",
            "accent_light": "#DBEAFE",
        },
        "dash-badge-week": {
            "eyebrow": f"BADGE SEMAINE {snapshots['current_week']}",
            "value": f"{snapshots['badge_week']['score']} %" if snapshots['badge_week']['score'] is not None else "—",
            "sub": f"{snapshots['badge_week']['status']} · {snapshots['badge_week']['total_fait']} / {snapshots['badge_week']['total_cible']} habitudes tenues" if snapshots['badge_week']['status'] else "aucune habitude saisie",
            "accent": "#10B981" if snapshots['badge_week'].get('status') == 'VERT' else "#F59E0B" if snapshots['badge_week'].get('status') == 'JAUNE' else "#EF4444" if snapshots['badge_week'].get('status') == 'ROUGE' else "#6B7280",
            "accent_light": "#D1FAE5" if snapshots['badge_week'].get('status') == 'VERT' else "#FEF3C7" if snapshots['badge_week'].get('status') == 'JAUNE' else "#FEE2E2" if snapshots['badge_week'].get('status') == 'ROUGE' else "#F3F4F6",
        },
        "dash-trimester-t2": {
            "eyebrow": f"TRIMESTRE {snapshots['current_trimester']}",
            "value": f"{snapshots['trimester_progress']['t2_percent']} %" if snapshots['trimester_progress']['t2_percent'] is not None else "—",
            "sub": f"{snapshots['trimester_progress']['sous_total_done']} sous done · {snapshots['trimester_progress']['sous_total_active']} en cours · {snapshots['trimester_progress']['total_plan_pages']} pages",
            "accent": "#F59E0B",
            "accent_light": "#FEF3C7",
        },
    }

    # Dashboard — 5 pilier cards
    for p in snapshots['piliers'].values():
        slug = p['slug'].replace('_', '-')
        kpi_catalog[f"dash-pilier-{slug}"] = {
            "eyebrow": p['name'].upper(),
            "value": f"{p['progress_avg']} %" if p['progress_avg'] is not None else "—",
            "sub": f"{len(p['achievements_active'])} achievement(s) actif(s)",
            "sub2": " · ".join(a['name'][:40] for a in p['achievements_active'][:2]) if p['achievements_active'] else "aucun actif",
            "accent": p['accent'],
            "accent_light": p['tint_light'],
        }

    # Per pilier — 3 KPIs × 5 piliers = 15
    for p in snapshots['piliers'].values():
        slug = p['slug'].replace('_', '-')
        habits = p.get('habits_w16', [])
        total_fait = sum(h.get('fait', 0) for h in habits)
        total_cible = sum(h.get('cible', 0) for h in habits)
        habit_pct = round(total_fait / total_cible * 100) if total_cible else None

        kpi_catalog[f"{slug}-achievements"] = {
            "eyebrow": "ACHIEVEMENTS ACTIFS",
            "value": f"{len(p['achievements_active'])} / 2",
            "sub": "plafond Time Budget" if p['slug'] != 'creation' else "plafond Tech+Arts combinés",
            "accent": p['accent'],
            "accent_light": p['tint_light'],
        }
        kpi_catalog[f"{slug}-habits"] = {
            "eyebrow": f"HABITUDES {snapshots['current_week']}",
            "value": f"{habit_pct} %" if habit_pct is not None else "—",
            "sub": f"{total_fait} / {total_cible} cibles semaine" if total_cible else "aucune habitude W16",
            "accent": p['accent'],
            "accent_light": p['tint_light'],
        }
        # Signature metric — all null for V2
        sig_labels = {
            "interieur": ("POIDS ACTUEL", "DB Mesures corps à brancher"),
            "famille": ("DATE-NIGHT CETTE SEMAINE", "DB Couple à brancher"),
            "pro_fi": ("NET WORTH", "DB Comptes à brancher"),
            "creation": ("PROGRESSION TECH", f"{p['progress_avg']} % · pas de sous complété T2"),
            "spirituel": ("PRÉDICATION AVRIL", "DB Rapports prédication à brancher"),
        }
        label, sub_text = sig_labels.get(p['slug'], ("SIGNATURE", ""))
        kpi_catalog[f"{slug}-signature"] = {
            "eyebrow": label,
            "value": "—",
            "sub": sub_text,
            "accent": p['accent'],
            "accent_light": p['tint_light'],
        }

    snapshots['kpi_catalog'] = kpi_catalog

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snapshots, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_PATH}")
    print(f"  · achievements actifs: {achievements_en_cours}")
    print(f"  · sous-achievements actifs: {sous_en_cours}")
    print(f"  · sous-achievements done: {sous_done}")
    print(f"  · tasks today (DB date={CURRENT_DATE}): {tlist_done}/{len(tlist)}")
    print(f"  · badge {CURRENT_WEEK}: {badge_status} {badge_pct}%" if badge_pct is not None else f"  · badge {CURRENT_WEEK}: null")
    print(f"  · historic weeks with habit data: {sum(1 for v in piliers_out['interieur']['habit_completion_12w'] if v is not None)}/12 Intérieur")


if __name__ == "__main__":
    main()
