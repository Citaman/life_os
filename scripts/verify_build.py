"""
Smoke-test generated Life OS artifacts.

Usage:
    python scripts/verify_build.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_PATH = REPO_ROOT / "data" / "snapshots.json"
DIST_PATH = REPO_ROOT / "dist"

REQUIRED_HTML = [
    "index.html",
    "kpi-pro-fi-signature.html",
    "achievements-pilier-pro-fi.html",
    "sous-achievements-pilier-pro-fi.html",
    "sankey-revenu-profi.html",
    "treemap-depenses-profi.html",
    "area-pilier-pro-fi.html",
    "gantt-pilier-pro-fi.html",
    "tasks-week-pilier-pro-fi.html",
    "journal-pilier-pro-fi.html",
    "treemap-transactions-account-anthonny.html",
    "history-transactions-account-anthonny.html",
    "treemap-transactions-account-mirane.html",
    "history-transactions-account-mirane.html",
]

REQUIRED_FINANCE_KEYS = [
    "month_key",
    "month_title",
    "cash_income_total",
    "budgeted_expenses",
    "projected_result",
    "estimated_end_balance",
    "income_lines",
    "expense_lines",
]

REQUIRED_TX_KEYS = [
    "account_name",
    "transaction_count",
    "months",
    "latest_month",
    "latest_month_totals",
    "expense_breakdowns_by_month",
    "monthly_history",
    "category_history",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    if not SNAPSHOTS_PATH.exists():
        fail(f"Missing {SNAPSHOTS_PATH}")
    if not DIST_PATH.exists():
        fail(f"Missing {DIST_PATH}")

    snapshots = json.loads(SNAPSHOTS_PATH.read_text())
    habits_context = snapshots.get("habits_week_context")
    if not habits_context:
        fail("habits_week_context missing from snapshots.json")
    for key in ("requested_week", "active_week", "latest_available_week", "used_fallback", "requested_row_count", "active_row_count"):
        if key not in habits_context:
            fail(f"habits_week_context missing key: {key}")

    active_habits_week = snapshots.get("active_habits_week")
    if not active_habits_week:
        fail("active_habits_week missing from snapshots.json")
    if habits_context["active_week"] != active_habits_week:
        fail("active_habits_week does not match habits_week_context.active_week")
    if habits_context["used_fallback"] and habits_context["active_week"] != habits_context["latest_available_week"]:
        fail("Habits fallback should resolve to latest_available_week")

    finance = snapshots.get("finance_current_month")
    if not finance:
        fail("finance_current_month missing from snapshots.json")

    for key in REQUIRED_FINANCE_KEYS:
        if key not in finance:
            fail(f"finance_current_month missing key: {key}")

    if not finance["income_lines"]:
        fail("finance_current_month.income_lines is empty")
    if not finance["expense_lines"]:
        fail("finance_current_month.expense_lines is empty")

    for filename in REQUIRED_HTML:
        path = DIST_PATH / filename
        if not path.exists():
            fail(f"Missing generated HTML: {path}")

    transactions = snapshots.get("transactions_accounts")
    if not transactions:
        fail("transactions_accounts missing from snapshots.json")

    for account_slug in ("anthonny", "mirane"):
        account = transactions.get(account_slug)
        if not account:
            fail(f"transactions_accounts.{account_slug} missing from snapshots.json")
        for key in REQUIRED_TX_KEYS:
            if key not in account:
                fail(f"transactions_accounts.{account_slug} missing key: {key}")
        if not account["months"]:
            fail(f"transactions_accounts.{account_slug}.months is empty")
        if not account["monthly_history"]:
            fail(f"transactions_accounts.{account_slug}.monthly_history is empty")
        if not account["expense_breakdowns_by_month"]:
            fail(f"transactions_accounts.{account_slug}.expense_breakdowns_by_month is empty")

    sankey_html = (DIST_PATH / "sankey-revenu-profi.html").read_text()
    month_title = str(finance["month_title"])
    if month_title not in sankey_html:
        fail("sankey-revenu-profi.html does not contain active month title")

    for account_slug in ("anthonny", "mirane"):
        account = transactions[account_slug]
        html = (DIST_PATH / f"treemap-transactions-account-{account_slug}.html").read_text()
        if account["account_name"] not in html:
            fail(f"treemap-transactions-account-{account_slug}.html missing account name")
        if account["latest_month"] not in html:
            fail(f"treemap-transactions-account-{account_slug}.html missing latest month")

    pro_fi = snapshots.get("piliers", {}).get("pro_fi")
    if not pro_fi:
        fail("piliers.pro_fi missing from snapshots.json")
    for key in ("habits_week_requested", "habits_week_used", "habits_week_is_fallback", "habits_w16", "habit_completion_12w", "roadmap", "journal_recent", "tasks_week_items", "achievements_active", "sous_achievements"):
        if key not in pro_fi:
            fail(f"piliers.pro_fi missing key: {key}")
    if not pro_fi.get("time_pilier"):
        fail("piliers.pro_fi.time_pilier missing from snapshots.json")
    if not pro_fi.get("roadmap"):
        fail("piliers.pro_fi.roadmap missing from snapshots.json")

    habits_kpi = snapshots.get("kpi_catalog", {}).get("pro-fi-habits")
    if not habits_kpi:
        fail("kpi_catalog.pro-fi-habits missing from snapshots.json")
    if active_habits_week not in str(habits_kpi.get("eyebrow", "")):
        fail("kpi_catalog.pro-fi-habits eyebrow does not mention active_habits_week")

    area_pilier_html = (DIST_PATH / "area-pilier-pro-fi.html").read_text()
    if "Pro &amp; Financier" not in area_pilier_html and "Pro & Financier" not in area_pilier_html:
        fail("area-pilier-pro-fi.html missing Pro & Financier context")
    if active_habits_week not in area_pilier_html:
        fail("area-pilier-pro-fi.html missing active habits week label")

    achievements_html = (DIST_PATH / "achievements-pilier-pro-fi.html").read_text()
    if "Achievements actifs" not in achievements_html:
        fail("achievements-pilier-pro-fi.html missing title")
    if "Budget familial maîtrisé" not in achievements_html:
        fail("achievements-pilier-pro-fi.html missing achievement content")

    sous_html = (DIST_PATH / "sous-achievements-pilier-pro-fi.html").read_text()
    if "Sous-achievements &amp; paliers" not in sous_html and "Sous-achievements & paliers" not in sous_html:
        fail("sous-achievements-pilier-pro-fi.html missing title")
    if "Choisir + installer outil tracker budget" not in sous_html:
        fail("sous-achievements-pilier-pro-fi.html missing sub-achievement content")

    tasks_html = (DIST_PATH / "tasks-week-pilier-pro-fi.html").read_text()
    if "liste pilotable + répartition par jour" not in tasks_html:
        fail("tasks-week-pilier-pro-fi.html missing planning subtitle")
    if "Pro &amp; Financier" not in tasks_html and "Pro & Financier" not in tasks_html:
        fail("tasks-week-pilier-pro-fi.html missing pilier name")
    if "Connecter tous les comptes bancaires" not in tasks_html:
        fail("tasks-week-pilier-pro-fi.html missing planned task list")

    gantt_html = (DIST_PATH / "gantt-pilier-pro-fi.html").read_text()
    if "Budget familial maîtrisé" not in gantt_html:
        fail("gantt-pilier-pro-fi.html missing roadmap content")
    if "Aujourd'hui" not in gantt_html:
        fail("gantt-pilier-pro-fi.html missing today marker")

    journal_html = (DIST_PATH / "journal-pilier-pro-fi.html").read_text()
    if "Journal Pro &amp; Financier" not in journal_html and "Journal Pro & Financier" not in journal_html:
        fail("journal-pilier-pro-fi.html missing title")
    if "Construction budget mai 2026" not in journal_html:
        fail("journal-pilier-pro-fi.html missing recent journal entry")
    if not pro_fi.get("journal_recent"):
        fail("piliers.pro_fi.journal_recent missing from snapshots.json")

    print("verify_build.py OK")
    print(
        "  habits:",
        f"requested={habits_context['requested_week']}",
        f"active={habits_context['active_week']}",
        f"fallback={habits_context['used_fallback']}",
    )
    print(
        "  finance:",
        finance["month_title"],
        f"revenus={finance['cash_income_total']}",
        f"dépenses={finance['budgeted_expenses']}",
        f"résultat={finance['projected_result']}",
    )
    for account_slug in ("anthonny", "mirane"):
        account = transactions[account_slug]
        print(
            "  transactions:",
            account["account_name"],
            f"mois={len(account['months'])}",
            f"latest={account['latest_month']}",
            f"rows={account['transaction_count']}",
        )


if __name__ == "__main__":
    main()
