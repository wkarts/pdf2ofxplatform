from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import AccountInfo, BankInfo, ExtractedDocument, Statement, Transaction
from pdf2ofx.domain.normalization import (
    classify_transaction,
    clean_text,
    create_fitid,
    infer_reference_year,
    normalize_ascii,
    parse_br_money,
)
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.helpers import TextLine, group_words_into_lines

_DATE_ONLY = re.compile(r"^\d{2}/\d{2}$")
_ACCOUNT_RE = re.compile(
    r"AGENCIA\s+CONTA\s+CORRENTE\s+(?P<branch>\d+)\s+(?P<account>[\d.-]+)",
    re.IGNORECASE | re.DOTALL,
)
_MONEY = re.compile(r"^\d{1,3}(?:\.\d{3})*,\d{2}-?$")


class SantanderParser(StatementParser):
    key = "santander"
    name = "Santander"

    def detect(self, document: ExtractedDocument) -> float:
        text = normalize_ascii(document.text)
        score = 0.0
        if "SANTANDER EMPRESAS" in text or "SANTANDER" in text:
            score += 0.6
        if "EXTRATO CONSOLIDADO INTELIGENTE" in text:
            score += 0.3
        if "CONTAMAX" in text:
            score += 0.1
        return min(score, 1.0)

    @staticmethod
    def _line_columns(line: TextLine) -> tuple[str | None, str, str | None, str | None, str | None]:
        date_text = clean_text(" ".join(word.text for word in line.words if word.x0 < 60))
        description = clean_text(
            " ".join(word.text for word in line.words if 60 <= word.x0 < 292)
        )
        document = clean_text(
            " ".join(word.text for word in line.words if 292 <= word.x0 < 365)
        )
        credit = clean_text(
            " ".join(word.text for word in line.words if 365 <= word.x0 < 425)
        )
        debit = clean_text(
            " ".join(word.text for word in line.words if 425 <= word.x0 < 505)
        )
        balance = clean_text(
            " ".join(word.text for word in line.words if word.x0 >= 505)
        )
        return (
            date_text if _DATE_ONLY.fullmatch(date_text) else None,
            description,
            document or None,
            credit or debit or None,
            balance or None,
        )

    def parse(self, document: ExtractedDocument) -> Statement:
        year = infer_reference_year(document.text)
        normalized_text = normalize_ascii(document.text)
        account_match = _ACCOUNT_RE.search(normalized_text)
        account = AccountInfo(
            branch=account_match.group("branch") if account_match else None,
            number=account_match.group("account") if account_match else None,
        )
        transactions: list[Transaction] = []
        current_date: date | None = None
        opening_balance: Decimal | None = None
        closing_balance: Decimal | None = None
        last_transaction: Transaction | None = None

        for line in group_words_into_lines(document.words, tolerance=3.2):
            if line.top < 48 or line.top > document.page_heights.get(line.page, 900) - 28:
                continue
            line_text = line.text
            normalized = normalize_ascii(line_text)
            if any(
                marker in normalized
                for marker in (
                    "DATA DESCRICAO",
                    "MOVIMENTOS (R$)",
                    "CREDITOS DEBITOS",
                    "EXTRATO_PJ_A4",
                    "PAGINA:",
                )
            ):
                continue
            (
                date_text,
                description,
                document_number,
                amount_raw,
                balance_raw,
            ) = self._line_columns(line)
            if date_text:
                day, month = (int(part) for part in date_text.split("/"))
                try:
                    current_date = date(year, month, day)
                except ValueError:
                    current_date = None

            if normalized.startswith("SALDO EM"):
                found = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", line_text)
                if found:
                    value = parse_br_money(found[-1])
                    if transactions:
                        closing_balance = value
                        break
                    opening_balance = value
                    closing_balance = value
                continue

            amount: Decimal | None = None
            if amount_raw:
                amount_token = amount_raw.replace(" ", "")
                money_match = next(
                    (token for token in amount_token.split() if _MONEY.fullmatch(token)),
                    None,
                ) or (amount_token if _MONEY.fullmatch(amount_token) else None)
                if money_match:
                    amount = parse_br_money(money_match)
                    # The Santander separates credit and debit by X coordinate.
                    amount_word = next(
                        (
                            word
                            for word in line.words
                            if _MONEY.fullmatch(word.text.replace(" ", ""))
                            and 365 <= word.x0 < 505
                        ),
                        None,
                    )
                    if amount_word is not None and amount_word.x0 >= 425 and amount > 0:
                        amount = -amount

            parsed_balance: Decimal | None = None
            if balance_raw:
                balance_tokens = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}-?", balance_raw)
                if balance_tokens:
                    parsed_balance = parse_br_money(balance_tokens[-1])
                    closing_balance = parsed_balance

            if amount is not None and current_date and description:
                description = clean_text(description.strip("- "))
                if not description:
                    continue
                transaction = Transaction(
                    posted_at=current_date,
                    description=description,
                    amount=amount,
                    document_number=(
                        None if document_number in {None, "-"} else document_number.strip("- ")
                    ),
                    balance=parsed_balance,
                    transaction_type=classify_transaction(description, amount),
                    source_page=line.page,
                    confidence=line.confidence,
                )
                transaction.fitid = create_fitid(
                    current_date,
                    amount,
                    description,
                    transaction.document_number,
                    len(transactions),
                )
                transactions.append(transaction)
                last_transaction = transaction
                continue

            # Santander prints beneficiary/origin on the next physical line.
            if (
                last_transaction
                and description
                and not amount_raw
                and not date_text
                and not normalized.startswith(("SALDO", "RESUMO", "CONTA CORRENTE"))
            ):
                continuation = clean_text(description)
                if continuation and continuation not in last_transaction.description:
                    last_transaction.description = clean_text(
                        f"{last_transaction.description} | {continuation}"
                    )

        if not transactions:
            raise ValueError("Nenhuma movimentação foi identificada no extrato Santander.")

        dates = [item.posted_at for item in transactions]
        confidence = sum(item.confidence for item in transactions) / len(transactions)
        return Statement(
            bank=BankInfo(code="033", name="Santander"),
            account=account,
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            confidence=min(0.99, confidence),
            source_parser=self.key,
        )
