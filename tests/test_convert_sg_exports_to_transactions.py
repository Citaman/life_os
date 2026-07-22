from __future__ import annotations

from scripts.convert_sg_exports_to_transactions import (
    attach_daily_balances,
    classify,
    classify_cost_nature,
)


def test_navigo_is_not_marked_recurring_even_for_monthly_amount():
    row = {
        "date": "2026-05-01",
        "amount": -90.80,
        "libelle": "CARTE X1234 30/04",
        "detail": "CARTE X1234 30/04 NAVIGO 123456789012",
    }

    converted = classify(row, "Anthonny")

    assert converted["merchant"] == "Navigo"
    assert converted["category"] == "Transport"
    assert converted["subcategory"] == "Public Transit"
    assert converted["is_recurring"] == "N"


def test_mirane_to_joint_outgoing_transfer_is_internal():
    row = {
        "date": "2026-06-05",
        "amount": -160.00,
        "libelle": "000001 VIR EUROPEE",
        "detail": (
            "000001 VIR EUROPEEN EMIS   LOGITEL POUR: M OLIME OU MME STOUPAN "
            "05 06 SG 03782 CPT 00057001522 REF: 9615670140840"
        ),
    }

    converted = classify(row, "Mirane")

    assert converted["merchant"] == "Mirane -> Compte joint"
    assert converted["category"] == "Transfers"
    assert converted["subcategory"] == "To Joint"
    assert converted["is_internal"] == "Y"


def test_joint_income_from_mirane_is_internal_transfer():
    row = {
        "date": "2026-06-05",
        "amount": 160.00,
        "libelle": "VIR RECU 961567014",
        "detail": "VIR RECU 9615670140840 DE: MME MIRANE OLIME",
    }

    converted = classify(row, "Joint")

    assert converted["merchant"] == "Mirane -> Compte joint"
    assert converted["category"] == "Transfers"
    assert converted["subcategory"] == "From Mirane"
    assert converted["is_internal"] == "Y"


def test_uber_trip_is_transport_not_food_delivery_or_shopping():
    row = {
        "date": "2026-07-10",
        "amount": -18.97,
        "libelle": "CARTE X0949 10/07",
        "detail": "CARTE X0949 10/07 UBER   *TRIP 18,97 EUR PAYS-BAS COMMERCE ELECTRONIQUE",
    }

    converted = classify(row, "Anthonny")

    assert converted["merchant"] == "Uber"
    assert converted["category"] == "Transport"
    assert converted["subcategory"] == "Ride Hailing"


def test_sodag_vending_is_food_not_general_shopping():
    row = {
        "date": "2026-07-10",
        "amount": -2.50,
        "libelle": "CARTE X0949 10/07",
        "detail": "CARTE X0949 10/07 SODAG 2,50 EUR FRANCE",
    }

    converted = classify(row, "Anthonny")

    assert converted["merchant"] == "SODAG"
    assert converted["category"] == "Food"
    assert converted["subcategory"] == "Coffee & Bakery"


def test_lpb_magenta_is_categorized_as_restaurant():
    row = {
        "date": "2026-06-18",
        "amount": -17.90,
        "libelle": "CARTE X0949 18/06",
        "detail": "CARTE X0949 18/06 LPB MAGENTA 17,90 EUR FRANCE",
    }

    converted = classify(row, "Anthonny")

    assert converted["merchant"] == "LPB Magenta"
    assert converted["category"] == "Food"
    assert converted["subcategory"] == "Restaurant"


def test_fbpm_is_categorized_as_clothing():
    row = {
        "date": "2026-05-24",
        "amount": -34.99,
        "libelle": "CARTE X0949 24/05",
        "detail": "CARTE X0949 24/05 FBPM 34,99 EUR FRANCE",
    }

    converted = classify(row, "Anthonny")

    assert converted["merchant"] == "FBPM"
    assert converted["category"] == "Shopping"
    assert converted["subcategory"] == "Clothing"


def test_cost_nature_separates_fixed_variable_and_ambiguous_expenses():
    assert classify_cost_nature(
        amount=-1193.94,
        category="Housing",
        subcategory="Rent",
        merchant="Loyer ORPI",
        recurring=True,
        internal=False,
    ) == "Fixe récurrent"
    assert classify_cost_nature(
        amount=-42.14,
        category="Food",
        subcategory="Delivery",
        merchant="Uber Eats",
        recurring=False,
        internal=False,
    ) == "Variable récurrent"
    assert classify_cost_nature(
        amount=-80,
        category="Cash",
        subcategory="ATM Withdrawal",
        merchant="Retrait DAB",
        recurring=False,
        internal=False,
    ) == "À vérifier"


def test_cost_nature_leaves_income_and_internal_transfers_blank():
    assert classify_cost_nature(
        amount=4000,
        category="Income",
        subcategory="Salary",
        merchant="Salaire DCF",
        recurring=True,
        internal=False,
    ) == ""
    assert classify_cost_nature(
        amount=-700,
        category="Transfers",
        subcategory="To Joint",
        merchant="Anthonny -> Compte joint",
        recurring=True,
        internal=True,
    ) == ""


def test_daily_balances_are_reconstructed_backwards_from_closing_balance():
    rows = [
        {"date": "2026-01-03", "amount": "-10.00", "daily_balance": ""},
        {"date": "2026-01-02", "amount": "20.00", "daily_balance": ""},
        {"date": "2026-01-01", "amount": "-5.00", "daily_balance": ""},
    ]

    attach_daily_balances(rows, closing_balance=100.0, balance_date="2026-01-03")

    assert [row["daily_balance"] for row in rows] == ["100.00", "110.00", "90.00"]
