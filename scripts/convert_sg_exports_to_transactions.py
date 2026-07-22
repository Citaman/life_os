"""Convert Societe Generale exports into the canonical Notion transaction format.

The generated CSV is a transient ingestion artifact. Notion remains the source of
truth after the idempotent import. Each transaction is categorized, and one row
per transaction day carries the account's end-of-day balance from the SG export.

Usage:
    python scripts/convert_sg_exports_to_transactions.py \
      --anthonny /path/to/Compte_Anthonny.csv \
      --joint /path/to/Compte_Join.csv \
      --output /tmp/life_os_transactions.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
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
    "daily_balance",
    "libelle",
    "detail",
]


@dataclass(frozen=True)
class SgExport:
    rows: list[dict[str, str]]
    balance_date: str
    closing_balance: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert SG exports to a Notion transaction import CSV.")
    parser.add_argument("--anthonny", required=True)
    parser.add_argument("--joint", required=True)
    parser.add_argument("--mirane")
    parser.add_argument("--anthonny-since", help="Optional ISO lower bound, for partial legacy imports only.")
    parser.add_argument("--mirane-since", help="Optional ISO lower bound, for partial legacy imports only.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_amount(raw: str) -> float:
    return float(raw.strip().replace("\xa0", "").replace(" ", "").replace("EUR", "").replace(",", "."))


def parse_date(raw: str) -> str:
    return datetime.strptime(raw.strip(), "%d/%m/%Y").date().isoformat()


def read_sg_export(path: Path) -> SgExport:
    text = path.read_text(encoding="latin-1")
    lines = text.splitlines()
    metadata = next(csv.reader([lines[0]], delimiter=";"))
    if len(metadata) < 2:
        raise ValueError(f"SG export metadata is missing in {path}")
    balance_date = parse_date(metadata[-2])
    closing_balance = parse_amount(metadata[-1])

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
    return SgExport(rows=rows, balance_date=balance_date, closing_balance=closing_balance)


def read_sg_csv(path: Path) -> list[dict[str, str]]:
    """Backward-compatible transaction-only reader used by tests and audits."""
    return read_sg_export(path).rows


def clean_card_merchant(detail: str) -> str:
    cleaned = re.sub(r"^CARTE X\d+\s+\d{2}/\d{2}\s+", "", detail).strip()
    cleaned = re.sub(r"\s+\d{12,}.*$", "", cleaned).strip()
    cleaned = re.sub(r"\s+COMMERCE ELECTRONIQUE.*$", "", cleaned).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned or "Carte"


def contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def classify(row: dict[str, str], account: str) -> dict[str, str]:
    detail = row["detail"]
    libelle = row["libelle"]
    upper = f"{libelle} {detail}".upper()
    amount = float(row["amount"])

    is_card = libelle.upper().startswith("CARTE X") and "RETRAIT DAB" not in upper
    merchant = clean_card_merchant(detail) if is_card else libelle.title()
    category = "Income" if amount > 0 else "Shopping"
    subcategory = "Other" if amount > 0 else "General"
    recurring = "N"
    internal = "N"

    if amount > 0:
        if "DIGITAL CLASSIFIED" in upper:
            merchant, subcategory, recurring = "Salaire DCF", "Salary", "Y"
        elif "OCTOPLUS" in upper or "RESTO-FLASH" in upper:
            merchant, subcategory, recurring = "Tickets resto (Octoplus)", "Benefits", "Y"
        elif "CAF" in upper:
            merchant, subcategory, recurring = "CAF", "Benefits", "Y"
        elif "MR ANTHONNY OLIME" in upper and account == "Joint":
            merchant, category, subcategory, internal = (
                "Anthonny -> Compte joint",
                "Transfers",
                "From Anthonny",
                "Y",
            )
        elif "MME MIRANE OLIME" in upper and account == "Joint":
            merchant, category, subcategory, internal = (
                "Mirane -> Compte joint",
                "Transfers",
                "From Mirane",
                "Y",
            )
        elif "MR ANTHONNY OLIME" in upper:
            merchant, category, subcategory, internal = "Remboursement Anthonny", "Transfers", "Internal", "Y"
        else:
            merchant = merchant.replace("Vir Recu", "Virement reçu")
    else:
        if "LOGITEL POUR: M OLIME OU MME STOUPAN" in upper:
            merchant = f"{account} -> Compte joint" if account in {"Anthonny", "Mirane"} else "Compte joint"
            category, subcategory, internal, recurring = "Transfers", "To Joint", "Y", "Y"
        elif "LOYER" in upper or "ORPI" in upper:
            merchant, category, subcategory, recurring = "Loyer ORPI", "Housing", "Rent", "Y"
        elif "BANQUE FRANCAISE MUTUALISTE" in upper or "CREDIT AUTO" in upper:
            merchant, category, subcategory, recurring = "Crédit auto compte joint", "Transport", "Car Loan", "Y"
        elif "FREE MOBILE" in upper:
            merchant, category, subcategory, recurring = "Free Mobile", "Bills", "Mobile", "Y"
        elif contains_any(upper, ("FREE TELECOM", "FREE HAUTDEBIT", "FREE BOX")):
            merchant, category, subcategory, recurring = "Free Box", "Bills", "Internet", "Y"
        elif "EDF" in upper:
            merchant, category, subcategory, recurring = "EDF", "Housing", "Utilities", "Y"
        elif "VEOLIA" in upper:
            merchant, category, subcategory, recurring = "Veolia", "Housing", "Utilities", "Y"
        elif contains_any(upper, ("MAIF", "CARDIF", "SOGESSUR", "ASSURANCE", "MATMUT", "PAPERNEST")):
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
                merchant = "Assurance habitation"
            category, subcategory, recurring = "Bills", "Insurance", "Y"
        elif "FNAC DARTY" in upper:
            merchant, category, subcategory, recurring = "Fnac Darty Services", "Bills", "Subscription", "Y"
        elif "FITNESS PARK" in upper:
            merchant, category, subcategory, recurring = "Fitness Park", "Entertainment", "Sports", "Y"
        elif contains_any(
            upper,
            (
                "JAZZ",
                "OPT INTL",
                "COTISATION",
                "FORFAIT RETRAITS",
                "FRAIS D'INCIDENTS",
                "ARRETE",
                "COMMISSION D'INTER",
                "INTERETS DEBITEURS",
                "LETTRE INFO COMPTE",
            ),
        ):
            merchant = "SG - frais bancaires"
            if "COTISATION" in upper:
                merchant = "SG - cotisation carte"
            category, subcategory = "Bills", "Bank Fees"
            recurring = "Y" if contains_any(upper, ("JAZZ", "OPT INTL", "FORFAIT RETRAITS")) else "N"
        elif contains_any(upper, ("BLOCAGE PROVISION", "AMENDES-TAX", "AMENDE.GOUV")):
            merchant, category, subcategory = "Trésor Public / amende", "Bills", "Fines"
        elif "RETRAIT DAB" in upper:
            merchant, category, subcategory = "Retrait DAB", "Cash", "ATM Withdrawal"
        elif contains_any(
            upper,
            (
                "ALDI",
                "LIDL",
                "CARREFOUR",
                "CARREF ",
                "FRANPRIX",
                "E.LECLERC",
                "INTERMARCHE",
                "MONOPRIX",
                "AUCHAN",
                "BADIS DISTRIB",
                "EUROCITY",
                "EDEKA",
                "ECP13085SUPERMAR",
                "DAC BONNEUIL EXPLOITATIO",
            ),
        ):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Food", "Groceries"
        elif contains_any(upper, ("UBER EATS", "EATS")):
            merchant, category, subcategory = "Uber Eats", "Food", "Delivery"
        elif contains_any(
            upper,
            (
                "MCDONALD",
                "MC DONALD",
                "BURGER KING",
                "BK BONNEUIL",
                "KFC",
                "QUICK",
                "FASTFOOD",
                "CCV*BURGER KING",
                "ZASOLEIL",
                "KAVI",
                "SWEET - FACTORY",
                "SESAME 66",
            ),
        ):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Food", "Fast Food"
        elif contains_any(
            upper,
            (
                "LEVAIN",
                "BOULANGERIE",
                "FOURNIL",
                "PAUL",
                "STARBUCKS",
                "SELECTA SAS",
                "AUX DELICES",
                "DELICES JUBIN",
                "MAXICOFFEE",
                "SBX3524POS",
                "MC THE",
                "SODAG",
            ),
        ):
            merchant = clean_card_merchant(detail).title()
            if "SODAG" in upper:
                merchant = "SODAG"
            category, subcategory = "Food", "Coffee & Bakery"
        elif contains_any(
            upper,
            (
                "SOLA RAMEN",
                "EAT SQUARE",
                "SC-SY EXPRESS",
                "LGH CRETEIL",
                "MESCAL",
                "SUSHI WAY",
                "COTE WOK",
                "BIG ZHAO",
                "BLACK BEANS",
                "ATELIER MALA",
                "DRAGON KING",
                "FIN.MONTMARTRE.R",
                "GRAND CAFE",
                "GUSTO",
                "JOE THE JUICE",
                "JOE  THE JUICE",
                "JUJIYA WAIZ",
                "MILTON",
                "NW GROUP",
                "Q154",
                "RESTO SAS",
                "SARL CEJYM",
                "SC-FETES A CREPES",
                "SC-RIQUET DIS",
                "SPINACH MFCO",
                "SUNDAY*SIR WINSTON",
                "TAILLEVENT",
                "CUISINE CRETEIL",
                "UBCE",
                "PARIS 2",
                "AMB",
                "QUIMPER",
                "LPB MAGENTA",
            ),
        ):
            merchant = clean_card_merchant(detail).title()
            if "LPB MAGENTA" in upper:
                merchant = "LPB Magenta"
            category, subcategory = "Food", "Restaurant"
        elif contains_any(upper, ("PHIE ", "PHARMACIE", "APOTHEKE")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Health", "Pharmacy"
        elif contains_any(upper, ("CDS QARE", "DR LASSAKER")):
            merchant = "Qare" if "QARE" in upper else clean_card_merchant(detail).title()
            category, subcategory = "Health", "Medical"
        elif contains_any(
            upper,
            ("TOTAL", "ESSO", "TEXACO", "CERTAS", "STAT AVIA", "RELAIS BONNEUIL", "RELAIS DE MONTAIGUT", "RELAIS LA SENTINELL", "SARL SJMC"),
        ):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Transport", "Fuel"
        elif "SANEF" in upper:
            merchant, category, subcategory = "SANEF", "Transport", "Tolls"
        elif contains_any(upper, ("EFFIA", "INDIGO", "PARKPLATZ", "DUESSELDORF PP HBF")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Transport", "Parking"
        elif contains_any(upper, ("AUTOBACS", "VSG LAVAGE AUTO")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Transport", "Car Care"
        elif "UBER" in upper and "*TRIP" in upper:
            merchant, category, subcategory = "Uber", "Transport", "Ride Hailing"
        elif "TRANSDEV" in upper or "NAVIGO" in upper:
            merchant, category, subcategory, recurring = "Navigo", "Transport", "Public Transit", "N"
        elif contains_any(upper, ("HYATT REGENCY", "THE NIU HUB", "CENTER PARCS")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Travel", "Lodging"
        elif contains_any(upper, ("AMAZON PRIME", "SPOTIFY")):
            merchant = "Amazon Prime" if "AMAZON PRIME" in upper else "Spotify"
            category, subcategory, recurring = "Entertainment", "Streaming", "Y"
        elif "AMZ DIGITAL" in upper:
            merchant, category, subcategory = "Amazon Digital", "Entertainment", "Digital Content"
        elif contains_any(upper, ("PATHE", "CINEMA")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Entertainment", "Cinema"
        elif contains_any(upper, ("PHANTASIALAND", "SMILE WORLD", "WGFA-ATTRACTIONS")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Entertainment", "Attractions"
        elif "EPPPD" in upper:
            merchant, category, subcategory = "Palais de la Porte Dorée", "Entertainment", "Museum"
        elif contains_any(upper, ("THEATRE MOGADOR", "T EVENT", "TICKETS")):
            merchant = "Billetterie" if "TICKETS" in upper else clean_card_merchant(detail).title()
            category, subcategory = "Entertainment", "Events"
        elif contains_any(upper, ("SPORTS INDOOR", "SALLE DE SPORT", "GYMLET")):
            merchant = "Salle de sport" if "SALLE DE SPORT" in upper else clean_card_merchant(detail).title()
            category, subcategory = "Entertainment", "Sports"
            recurring = "Y" if "SALLE DE SPORT" in upper else "N"
        elif contains_any(upper, ("REGIE ENFANCENET", "AGCME")):
            merchant = clean_card_merchant(detail).title()
            if "AGCME" in upper:
                merchant = "AGCME"
            category, subcategory = "Family", "Childcare"
        elif "SMYTHS TOYS" in upper:
            merchant, category, subcategory = "Smyths Toys", "Family", "Toys"
        elif contains_any(upper, ("AMAZON PAYMENTS", "AMAZON EU SARL")):
            merchant, category, subcategory = "Amazon", "Shopping", "Online"
        elif contains_any(upper, ("PRIMARK", "STRADIVARIUS", "C ET A", "DEICHMANN", "JD  PARIS", "KIABI", "NAUMY", "VS CRETEIL", "FBPM")):
            merchant = clean_card_merchant(detail).title()
            if "FBPM" in upper:
                merchant = "FBPM"
            category, subcategory = "Shopping", "Clothing"
        elif contains_any(upper, ("FNAC", "INTERSPORT", "ZETTLE_*COMMERCE & CO")):
            merchant = clean_card_merchant(detail).title()
            if "ZETTLE_*COMMERCE & CO" in upper:
                merchant = "Commerce & Co"
            category, subcategory = "Shopping", "Electronics & Leisure"
        elif contains_any(upper, ("MATY", "LOVISA")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Shopping", "Jewelry"
        elif contains_any(upper, ("LEROY", "ADEO")):
            merchant, category, subcategory = "Leroy Merlin", "Home", "DIY"
        elif contains_any(upper, ("MYE BEAUTY", "YVES ROCHER")):
            merchant = clean_card_merchant(detail).title()
            category, subcategory = "Personal Care", "Beauty"
        elif "Y&R COIFFURE" in upper:
            merchant, category, subcategory = "Y&R Coiffure", "Personal Care", "Hairdresser"
        elif "5 A SEC" in upper:
            merchant, category, subcategory = "5 à Sec", "Personal Care", "Laundry"
        elif "REAPHOT" in upper:
            merchant, category, subcategory = "Reaphot", "Personal Care", "Photo"
        elif "PAYFIP" in upper:
            merchant, category, subcategory = "PayFiP Bonneuil", "Bills", "Local Government"
        elif "LA POSTE" in upper:
            merchant, category, subcategory = "La Poste", "Bills", "Postal"
        elif "LYDIA*POT DE DEPART" in upper:
            merchant, category, subcategory = "Pot de départ", "Gifts", "Gift"
        elif "WERO" in upper or "VIR INSTANTANE EMIS" in upper or "VIR EUROPEEN EMIS" in upper:
            merchant, category, subcategory = "Virement sortant", "Transfers", "To Others"
        elif contains_any(upper, ("ACTION ", "NORMAL ", "HEMA", "CRETEIL SOLEIL", "WESTFIELD", "TILLI TILLI", "ODISCOUNT", "L OU EXPERT")):
            merchant = clean_card_merchant(detail).title()
            if "L OU EXPERT" in upper:
                merchant = "L OU Expert"
            category, subcategory = "Shopping", "General"
        else:
            # A complete taxonomy is preferable to an unusable Uncategorized bucket.
            # Unknown card merchants remain reviewable in Notion under Shopping/General;
            # unknown non-card debits are grouped as other bills.
            merchant = clean_card_merchant(detail) if is_card else merchant
            if not is_card:
                category, subcategory = "Bills", "Other"

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
        "daily_balance": "",
        "libelle": libelle,
        "detail": detail,
    }


def attach_daily_balances(rows: list[dict[str, str]], closing_balance: float, balance_date: str) -> None:
    """Attach an SG end-of-day balance to one deterministic transaction per date."""
    totals_by_date: dict[str, float] = {}
    for row in rows:
        if row["date"] <= balance_date:
            totals_by_date[row["date"]] = totals_by_date.get(row["date"], 0.0) + float(row["amount"])

    balance_by_date: dict[str, float] = {}
    later_activity = 0.0
    for day in sorted(totals_by_date, reverse=True):
        balance_by_date[day] = round(closing_balance - later_activity, 2)
        later_activity += totals_by_date[day]

    marked_dates: set[str] = set()
    for row in rows:
        day = row["date"]
        if day in balance_by_date and day not in marked_dates:
            row["daily_balance"] = f"{balance_by_date[day]:.2f}"
            marked_dates.add(day)


def convert_account(export: SgExport, account: str, since: str | None = None) -> list[dict[str, str]]:
    rows = [classify(row, account) for row in export.rows]
    attach_daily_balances(rows, export.closing_balance, export.balance_date)
    if since:
        rows = [row for row in rows if row["date"] >= since]
    return rows


def main() -> None:
    args = parse_args()
    out_path = Path(args.output)
    rows: list[dict[str, str]] = []

    rows.extend(convert_account(read_sg_export(Path(args.anthonny)), "Anthonny", args.anthonny_since))
    rows.extend(convert_account(read_sg_export(Path(args.joint)), "Joint"))
    if args.mirane:
        rows.extend(convert_account(read_sg_export(Path(args.mirane)), "Mirane", args.mirane_since))

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
