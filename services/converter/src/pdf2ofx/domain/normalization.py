from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

MONEY_RE = re.compile(r"[-+]?\s*(?:R\$\s*)?\d{1,3}(?:\.\d{3})*,\d{2}[+-]?")
DATE_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()


def normalize_ascii(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).upper()


def parse_br_money(value: str) -> Decimal:
    raw = clean_text(value).replace("R$", "").replace(" ", "")
    trailing_sign = raw[-1:] if raw[-1:] in {"+", "-"} else ""
    if trailing_sign:
        raw = raw[:-1]
    negative = raw.startswith("-") or trailing_sign == "-"
    raw = raw.lstrip("+-").replace(".", "").replace(",", ".")
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"Valor monetário inválido: {value}") from exc
    return -amount if negative else amount


def parse_date(value: str, default_year: int, default_month: int | None = None) -> date:
    match = DATE_RE.search(value)
    if not match:
        raise ValueError(f"Data inválida: {value}")
    day = int(match.group(1))
    month = int(match.group(2)) if match.group(2) else int(default_month or 1)
    year_raw = match.group(3)
    year = default_year
    if year_raw:
        year = int(year_raw)
        if year < 100:
            year += 2000
    return date(year, month, day)


def classify_transaction(description: str, amount: Decimal) -> str:
    text = normalize_ascii(description)
    if amount > 0:
        if any(term in text for term in ("PIX", "TED", "TRANSFER", "RECEB", "DEPOS")):
            return "CREDIT"
        if "RENDIMENTO" in text:
            return "INT"
        return "CREDIT"
    if any(term in text for term in ("TARIFA", "IOF", "JUROS", "ENCARGO")):
        return "FEE"
    if any(term in text for term in ("BOLETO", "PAGAMENTO", "PGTO", "PIX", "TED", "TRANSFER")):
        return "DEBIT"
    if "CHEQUE" in text:
        return "CHECK"
    return "DEBIT"


def create_fitid(
    transaction_date: date,
    amount: Decimal,
    description: str,
    document_number: str | None,
    ordinal: int,
) -> str:
    material = "|".join(
        (
            transaction_date.isoformat(),
            f"{amount:.2f}",
            clean_text(description),
            document_number or "",
            str(ordinal),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32].upper()


def infer_reference_year(text: str) -> int:
    normalized = normalize_ascii(text)
    contextual = re.search(
        r"(?:JANEIRO|FEVEREIRO|MARCO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|"
        r"SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)\s*/\s*(20\d{2})",
        normalized,
    )
    if contextual:
        return int(contextual.group(1))
    full_date = re.search(r"\b\d{1,2}/\d{1,2}/(20\d{2})\b", text)
    if full_date:
        return int(full_date.group(1))
    matches = re.findall(r"\b20\d{2}\b", text)
    if matches:
        counts = {value: matches.count(value) for value in set(matches)}
        return int(max(counts, key=counts.get))
    return datetime.now().year


def infer_reference_month(text: str) -> int | None:
    ascii_text = normalize_ascii(text)
    months = {
        "JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "ABRIL": 4,
        "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
        "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
    }
    for name, number in months.items():
        if name in ascii_text:
            return number
    month_year = re.search(r"\b(0?[1-9]|1[0-2])/20\d{2}\b", text)
    return int(month_year.group(1)) if month_year else None
