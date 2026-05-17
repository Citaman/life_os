from __future__ import annotations

import hashlib
import importlib
import sys
import types


def import_transaction_importer(monkeypatch):
    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *args, **kwargs: None

    fake_notion = types.ModuleType("notion_client")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

    fake_notion.Client = DummyClient

    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)
    monkeypatch.setitem(sys.modules, "notion_client", fake_notion)
    monkeypatch.setenv("NOTION_TOKEN", "unit-test-token")
    sys.modules.pop("scripts.import_transactions_to_notion", None)
    return importlib.import_module("scripts.import_transactions_to_notion")


def test_source_key_is_stable_sha1_of_identity_fields(monkeypatch):
    importer = import_transaction_importer(monkeypatch)
    row = {
        "account": "Anthonny",
        "date": "2026-04-01",
        "amount": "-12.34",
        "direction": "debit",
        "merchant": "Merchant",
        "libelle": "Libelle",
        "detail": "Detail",
        "category": "Ignored",
    }

    expected_raw = "Anthonny||2026-04-01||-12.34||debit||Merchant||Libelle||Detail"
    assert importer.source_key(row) == hashlib.sha1(expected_raw.encode("utf-8")).hexdigest()


def test_source_key_defaults_missing_fields_to_empty_strings(monkeypatch):
    importer = import_transaction_importer(monkeypatch)

    expected_raw = "Mirane||||||||||||"
    assert importer.source_key({"account": "Mirane"}) == hashlib.sha1(expected_raw.encode("utf-8")).hexdigest()


def test_identity_key_ignores_merchant_and_category(monkeypatch):
    importer = import_transaction_importer(monkeypatch)

    base = {
        "Date": "2026-04-23",
        "Montant": -20,
        "Direction": "expense",
        "Libellé": "CARTE X7234 22/04",
        "Détail": "CARTE X7234 22/04 RELAIS DE MONTAIGUT 110611300848454IOPD",
        "Marchand": "Old merchant",
        "Catégorie": "Uncategorized",
    }
    corrected = {
        **base,
        "Montant": "-20.00",
        "Marchand": "Corrected merchant",
        "Catégorie": "Food",
    }

    assert importer.identity_key(base) == importer.identity_key(corrected)
