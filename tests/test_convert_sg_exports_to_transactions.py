from __future__ import annotations

from scripts.convert_sg_exports_to_transactions import attach_daily_balances, classify


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


def test_daily_balances_are_reconstructed_backwards_from_closing_balance():
    rows = [
        {"date": "2026-01-03", "amount": "-10.00", "daily_balance": ""},
        {"date": "2026-01-02", "amount": "20.00", "daily_balance": ""},
        {"date": "2026-01-01", "amount": "-5.00", "daily_balance": ""},
    ]

    attach_daily_balances(rows, closing_balance=100.0, balance_date="2026-01-03")

    assert [row["daily_balance"] for row in rows] == ["100.00", "110.00", "90.00"]
