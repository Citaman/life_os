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

    sankey_html = (DIST_PATH / "sankey-revenu-profi.html").read_text()
    month_title = str(finance["month_title"])
    if month_title not in sankey_html:
        fail("sankey-revenu-profi.html does not contain active month title")

    print("verify_build.py OK")
    print(
        "  finance:",
        finance["month_title"],
        f"revenus={finance['cash_income_total']}",
        f"dépenses={finance['budgeted_expenses']}",
        f"résultat={finance['projected_result']}",
    )


if __name__ == "__main__":
    main()
