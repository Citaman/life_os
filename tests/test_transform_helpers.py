from __future__ import annotations

import importlib
import sys
import types
from datetime import date


def import_transform(monkeypatch):
    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)
    sys.modules.pop("scripts.transform", None)
    return importlib.import_module("scripts.transform")


def test_safe_number_accepts_numeric_inputs(monkeypatch):
    transform = import_transform(monkeypatch)

    assert transform.safe_number("42") == 42.0
    assert transform.safe_number(" 3.5 ") == 3.5
    assert transform.safe_number(7) == 7.0
    assert transform.safe_number(2.25) == 2.25


def test_safe_number_returns_none_for_blank_or_invalid_values(monkeypatch):
    transform = import_transform(monkeypatch)

    assert transform.safe_number(None) is None
    assert transform.safe_number("") is None
    assert transform.safe_number("not-a-number") is None
    assert transform.safe_number(object()) is None


def test_parse_percent_extracts_explicit_percentage(monkeypatch):
    transform = import_transform(monkeypatch)

    assert transform.parse_percent("75%") == 75
    assert transform.parse_percent("Progression actuelle: 12 %") == 12
    assert transform.parse_percent("100% puis 50%") == 100
    assert transform.parse_percent("aucun pourcentage") is None
    assert transform.parse_percent(None) is None


def test_week_helpers_parse_and_build_stable_ranges(monkeypatch):
    transform = import_transform(monkeypatch)

    assert transform.parse_week_number("w16") == 16
    assert transform.parse_week_number(" W05 ") == 5
    assert transform.parse_week_number("2026-W16") is None
    assert transform.parse_week_number(None) is None
    assert transform.build_historic_weeks("W04", span=3) == ["W02", "W03", "W04"]
    monkeypatch.setattr(transform, "CURRENT_DATE_OBJ", date(2026, 4, 19))
    assert transform.build_historic_weeks(None, span=2) == ["W15", "W16"]


def test_resolve_habits_week_uses_latest_available_when_requested_week_missing(monkeypatch):
    transform = import_transform(monkeypatch)
    habits = [
        {"Semaine": "W14", "Pilier": "Pro & Financier"},
        {"Semaine": "w16", "Pilier": "Pro & Financier"},
        {"Semaine": "W16", "Pilier": "Famille"},
    ]

    assert transform.latest_habits_week(habits) == "W16"
    assert transform.resolve_habits_week(habits, "W15") == {
        "requested_week": "W15",
        "active_week": "W16",
        "latest_available_week": "W16",
        "used_fallback": True,
        "requested_row_count": 0,
        "active_row_count": 2,
    }


def test_month_key_from_page_uses_explicit_period_or_title(monkeypatch):
    transform = import_transform(monkeypatch)

    assert transform.month_key_from_page({"Mois clé": "2026-04"}) == "2026-04"
    assert transform.month_key_from_page({"Période": {"start": "2026-05-01"}}) == "2026-05"
    assert transform.month_key_from_page({"Mois": "2026-06 Budget"}) == "2026-06"
    assert transform.month_key_from_page({"Mois": "Budget juin"}) is None
