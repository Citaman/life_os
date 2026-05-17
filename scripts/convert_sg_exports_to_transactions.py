"""
Convert Societe Generale CSV exports into the consolidated transaction CSV format.

This is intentionally conservative: it imports only new Anthonny rows from
2026-04-21 onward, while the newly created Joint account gets the full export.

Usage:
    python scripts/convert_sg_exports_to_transactions.py \
      --anthonny /path/to/Compte_Anthonny.csv \
      --joint /path/to/Compte_Join.csv \
      --output data/import_2026-04-28_bank_transactions.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path


HEADERS = [
    "account",
    "date",
    "amount",
    "direction",
    "merchant",
    "category",
    "subcategory",
    "is_recurring",
    "is_internal",
    "auto_categorized",
    "libelle",
    "detail",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert SG exports to life_os transaction import CSV.")
    parser.add_argument("--anthonny", required=True)
    parser.add_argument("--joint", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_amount(raw: str) -> float:
    return float(raw.strip().replace("\xa0", "").replace(" ", "").replace(",", "."))


def parse_date(raw: str) -> str:
    return datetime.strptime(raw.strip(), "%d/%m/%Y").date().isoformat()


def read_sg_csv(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="latin-1")
    lines = text.splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith("Date de l'op"))
    reader = csv.DictReader(lines[header_index:], delimiter=";")
    rows = []
    for row in reader:
        if not row.get("Date de l'opération"):
            continue
        rows.append(
            {
                "date": parse_date(row["Date de l'opération"]),
                "libelle": (row.get("Libellé") or "").strip(),
                "detail": (row.get("Détail de l'écriture") or "").strip(),
                "amount": parse_amount(row["Montant de l'opération"]),
            }
        )
    return rows


def clean_card_merchant(detail: str) -> str:
    cleaned = re.sub(r"^CARTE X\d+\s+\d{2}/\d{2}\s+", "", detail).strip()
    cleaned = re.sub(r"\s+\d{12,}.*$", "", cleaned).strip()
    cleaned = re.sub(r"\s+COMMERCE ELECTRONIQUE.*$", "", cleaned).strip()
    cleaned = cleaned.replace("  ", " ")
    return cleaned or "Carte"


def classify(row: dict[str, str], account: str) -> dict[str, str]:
    detail = row["detail"]
    libelle = row["libelle"]
    upper = f"{libelle} {detail}".upper()
    amount = row["amount"]

    merchant = clean_card_merchant(detail) if "CARTE X" in upper else libelle.title()
    category = "Uncategorized"
    subcategory = "Unknown"
    recurring = "N"
    internal = "N"

    if amount > 0:
        category = "Income"
        subcategory = "Other"
        if "DIGITAL CLASSIFIED" in upper:
            merchant = "Salaire DCF"
            subcategory = "Salary"
            recurring = "Y"
        elif "OCTOPLUS" in upper or "RESTO-FLASH" in upper:
            merchant = "Tickets resto (Octoplus)"
            subcategory = "Benefits"
            recurring = "Y"
        elif "CAF" in upper:
            merchant = "CAF"
            subcategory = "Benefits"
            recurring = "Y"
        elif "MR ANTHONNY OLIME" in upper and account == "Joint":
            merchant = "Anthonny -> Compte joint"
            category = "Transfers"
            subcategory = "From Anthonny"
            internal = "Y"
        elif "MR ANTHONNY OLIME" in upper:
            merchant = "Remboursement Anthonny"
            category = "Transfers"
            subcategory = "Internal"
            internal = "Y"
        else:
            merchant = merchant.replace("Vir Recu", "Virement reçu")
    else:
        if "LOGITEL POUR: M OLIME OU MME STOUPAN" in upper:
            merchant = "Anthonny -> Compte joint"
            category = "Transfers"
            subcategory = "To Joint"
            internal = "Y"
            recurring = "Y"
        elif "LOYER" in upper or "ORPI" in upper:
            merchant = "Loyer ORPI"
            category = "Housing"
            subcategory = "Rent"
            recurring = "Y"
        elif "BANQUE FRANCAISE MUTUALISTE" in upper or "CREDIT AUTO" in upper:
            merchant = "Crédit auto compte joint"
            category = "Transport"
            subcategory = "Car Loan"
            recurring = "Y"
        elif "FREE MOBILE" in upper:
            merchant = "Free Mobile"
            category = "Bills"
            subcategory = "Mobile"
            recurring = "Y"
        elif "FREE TELECOM" in upper or "FREE HAUTDEBIT" in upper or "FREE BOX" in upper:
            merchant = "Free Box"
            category = "Bills"
            subcategory = "Internet"
            recurring = "Y"
        elif "EDF" in upper:
            merchant = "EDF"
            category = "Housing"
            subcategory = "Utilities"
            recurring = "Y"
        elif "VEOLIA" in upper:
            merchant = "Veolia"
            category = "Housing"
            subcategory = "Utilities"
            recurring = "Y"
        elif any(token in upper for token in ("MAIF", "CARDIF", "SOGESSUR", "ASSURANCE", "MATMUT", "PAPERNEST")):
            merchant = "Assurance"
            if "CARDIF" in upper:
                merchant = "Cardif"
            elif "MAIF VIE" in upper:
                merchant = "MAIF Vie"
            elif "MAIF" in upper:
                merchant = "MAIF"
            elif "SOGESSUR" in upper:
                merchant = "Sogessur"
            elif "PAPERNEST" in upper:
                merchant = "Assurance Habitation"
            category = "Bills"
            subcategory = "Insurance"
            recurring = "Y"
        elif any(token in upper for token in ("JAZZ", "OPT INTL", "COTISATION", "FORFAIT RETRAITS", "FRAIS D'INCIDENTS", "ARRETE")):
            merchant = "SG - frais bancaires"
            if "COTISATION" in upper:
                merchant = "SG - cotisation carte"
            category = "Bills"
            subcategory = "Bank Fees"
            recurring = "Y" if any(token in upper for token in ("JAZZ", "OPT INTL", "FORFAIT RETRAITS")) else "N"
        elif "BLOCAGE PROVISION" in upper or "AMENDES-TAX" in upper:
            merchant = "Trésor Public / amende"
            category = "Bills"
            subcategory = "Fines"
        elif any(token in upper for token in ("ALDI", "LIDL", "CARREFOUR", "CARREF ", "FRANPRIX")):
            merchant = "Aldi" if "ALDI" in upper else ("Lidl" if "LIDL" in upper else "Carrefour")
            category = "Food"
            subcategory = "Groceries"
        elif any(token in upper for token in ("UBER", "EATS")):
            merchant = "Uber Eats"
            category = "Food"
            subcategory = "Delivery"
        elif any(token in upper for token in ("MCDONALD", "KAVI", "SWEET", "SESAME", "BIG FERNAND")):
            merchant = "Kavi" if "KAVI" in upper else clean_card_merchant(detail).title()
            category = "Food"
            subcategory = "Fast Food"
        elif any(token in upper for token in ("LEVAIN", "BOULANGERIE", "FOURNIL", "PAUL")):
            merchant = "Boulangerie" if "BOULANGERIE" in upper or "FOURNIL" in upper else "Levain"
            category = "Food"
            subcategory = "Coffee & Bakery"
        elif "LEROY" in upper or "ADEO" in upper:
            merchant = "Leroy Merlin"
            category = "Home"
            subcategory = "DIY"
        elif "SPORTS INDOOR" in upper or "SALLE DE SPORT" in upper:
            merchant = "Salle de sport"
            category = "Entertainment"
            subcategory = "Sports"
            recurring = "Y" if "SALLE DE SPORT" in upper else "N"
        elif "TRANSDEV" in upper or "NAVIGO" in upper:
            merchant = "Navigo"
            category = "Transport"
            subcategory = "Public Transit"
            recurring = "Y" if abs(amount) >= 80 else "N"
        elif "WERO" in upper or "VIR INSTANTANE EMIS" in upper or "VIR EUROPEEN EMIS" in upper:
            merchant = "Virement sortant"
            category = "Transfers"
            subcategory = "To Others"
        else:
            merchant = clean_card_merchant(detail) if "CARTE X" in upper else merchant

    return {
        "account": account,
        "date": row["date"],
        "amount": f"{amount:.2f}",
        "direction": "income" if amount > 0 else "expense",
        "merchant": merchant.strip(),
        "category": category,
        "subcategory": subcategory,
        "is_recurring": recurring,
        "is_internal": internal,
        "auto_categorized": "Y",
        "libelle": libelle,
        "detail": detail,
    }


def main() -> None:
    args = parse_args()
    out_path = Path(args.output)
    rows: list[dict[str, str]] = []

    for row in read_sg_csv(Path(args.anthonny)):
        if row["date"] >= "2026-04-21":
            rows.append(classify(row, "Anthonny"))

    for row in read_sg_csv(Path(args.joint)):
        rows.append(classify(row, "Joint"))

    rows.sort(key=lambda item: (item["account"], item["date"], item["amount"], item["detail"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["account"]] = counts.get(row["account"], 0) + 1
    print(f"Wrote {out_path} — {counts}")


if __name__ == "__main__":
    main()
