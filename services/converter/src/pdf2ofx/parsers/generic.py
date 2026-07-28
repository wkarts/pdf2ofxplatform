from __future__ import annotations

import re
from datetime import date

from pdf2ofx.domain.models import AccountInfo, BankInfo, ExtractedDocument, Statement, Transaction
from pdf2ofx.domain.normalization import (
    classify_transaction,
    clean_text,
    create_fitid,
    infer_reference_year,
    parse_br_money,
)
from pdf2ofx.parsers.base import StatementParser

_LINE = re.compile(
    r"^\s*(?P<date>\d{2}/\d{2}(?:/\d{2,4})?)\s+"
    r"(?P<description>.+?)\s+"
    r"(?P<amount>[-+]?\d{1,3}(?:\.\d{3})*,\d{2}[+-]?)"
    r"(?:\s+(?P<balance>[-+]?\d{1,3}(?:\.\d{3})*,\d{2}))?\s*$"
)


class GenericParser(StatementParser):
    key = "generic"
    name = "Layout genérico"

    def detect(self, document: ExtractedDocument) -> float:
        matches = sum(1 for line in document.text.splitlines() if _LINE.match(line))
        return min(0.45, matches / 30)

    def parse(self, document: ExtractedDocument) -> Statement:
        default_year = infer_reference_year(document.text)
        transactions: list[Transaction] = []
        for line_number, line in enumerate(document.text.splitlines(), start=1):
            match = _LINE.match(clean_text(line))
            if not match:
                continue
            date_parts = [int(item) for item in match.group("date").split("/")]
            day, month = date_parts[0], date_parts[1]
            year = date_parts[2] if len(date_parts) == 3 else default_year
            if year < 100:
                year += 2000
            try:
                posted_at = date(year, month, day)
                amount = parse_br_money(match.group("amount"))
                balance = (
                    parse_br_money(match.group("balance"))
                    if match.group("balance")
                    else None
                )
            except ValueError:
                continue
            description = clean_text(match.group("description"))
            transaction = Transaction(
                posted_at=posted_at,
                description=description,
                amount=amount,
                balance=balance,
                transaction_type=classify_transaction(description, amount),
                source_page=1,
                confidence=0.65,
            )
            transaction.fitid = create_fitid(posted_at, amount, description, None, line_number)
            transactions.append(transaction)

        if not transactions:
            raise ValueError("O layout genérico não encontrou linhas de transação.")
        dates = [item.posted_at for item in transactions]
        return Statement(
            bank=BankInfo(code="000", name="Banco não identificado"),
            account=AccountInfo(),
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            closing_balance=transactions[-1].balance,
            confidence=0.65,
            warnings=["Banco não identificado automaticamente; revise todas as transações."],
            source_parser=self.key,
        )
