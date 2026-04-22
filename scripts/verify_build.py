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
    "sankey-revenu-profi.html",
    "treemap-depenses-profi.html",
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

    print("verify_build.py OK")
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
