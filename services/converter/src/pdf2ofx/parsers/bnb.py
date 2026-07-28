from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import AccountInfo, BankInfo, ExtractedDocument, Statement, Transaction
from pdf2ofx.domain.normalization import (
    classify_transaction,
    clean_text,
    create_fitid,
    infer_reference_month,
    infer_reference_year,
    normalize_ascii,
    parse_br_money,
)
from pdf2ofx.parsers.base import StatementParser

_ROW_RE = re.compile(
    r"^\s*(?:(?P<day>\d{1,2})\s+)?"
    r"(?P<description>.+?)\s+"
    r"(?P<document>[A-Za-z0-9./*-]+)\s+"
    r"(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2}[+-])"
    r"(?:\s+(?P<balance>\d{1,3}(?:\.\d{3})*,\d{2}))?\s*$"
)
_ACCOUNT_RE = re.compile(
    r"AGENCIA:\s*(?P<branch>\d+)\s+CONTA\s+(?P<account>[\d.-]+)",
    re.IGNORECASE,
)


class BnbParser(StatementParser):
    key = "bnb"
    name = "Banco do Nordeste"

    def detect(self, document: ExtractedDocument) -> float:
        text = normalize_ascii(document.text)
        score = 0.0
        if "BANCO DO NORDESTE" in text or "INTERNET BANKING BNB" in text:
            score += 0.65
        if "DEMONSTRATIVO DA MOVIMENTACAO DE CONTA CORRENTE" in text:
            score += 0.25
        if "RECEBIMENTO VIA PIX" in text and "DEBITO PRINCIPAL" in text:
            score += 0.1
        return min(score, 1.0)

    def parse(self, document: ExtractedDocument) -> Statement:
        year = infer_reference_year(document.text)
        month = infer_reference_month(document.text) or 1
        account_match = _ACCOUNT_RE.search(normalize_ascii(document.text))
        account = AccountInfo(
            branch=account_match.group("branch") if account_match else None,
            number=account_match.group("account") if account_match else None,
        )

        lines = [clean_text(line) for line in document.text.splitlines() if clean_text(line)]
        in_section = False
        current_day: int | None = None
        transactions: list[Transaction] = []
        opening_balance: Decimal | None = None
        last_balance: Decimal | None = None

        for line in lines:
            normalized = normalize_ascii(line)
            if "DEMONSTRATIVO DA MOVIMENTACAO DE CONTA CORRENTE" in normalized:
                in_section = True
                continue
            if in_section and any(
                marker in normalized
                for marker in (
                    "RELACAO DE CHEQUES EM ORDEM",
                    "MOVIMENTACOES EM APLICACOES",
                    "APLICACOES FINANCEIRAS",
                )
            ):
                break
            if not in_section:
                continue
            if normalized.startswith(("DIA HISTORICO", "_", "HTTP")):
                continue
            if normalized.startswith("SALDO ANTERIOR"):
                money = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", line)
                if money:
                    opening_balance = parse_br_money(money[-1])
                    last_balance = opening_balance
                continue

            match = _ROW_RE.match(line)
            if not match:
                continue
            day_raw = match.group("day")
            if day_raw:
                current_day = int(day_raw)
            if current_day is None:
                continue
            try:
                posted_at = date(year, month, current_day)
                amount = parse_br_money(match.group("amount"))
                balance_raw = match.group("balance")
                balance = parse_br_money(balance_raw) if balance_raw else None
            except (ValueError, OverflowError):
                continue

            description = clean_text(match.group("description"))
            if normalize_ascii(description).startswith("SALDO "):
                continue
            transaction = Transaction(
                posted_at=posted_at,
                description=description,
                amount=amount,
                document_number=match.group("document"),
                balance=balance,
                transaction_type=classify_transaction(description, amount),
                source_page=1,
                confidence=0.97,
            )
            transaction.fitid = create_fitid(
                posted_at, amount, description, transaction.document_number, len(transactions)
            )
            transactions.append(transaction)
            if balance is not None:
                last_balance = balance

        if not transactions:
            raise ValueError(
                "Nenhuma movimentação de conta corrente foi identificada "
                "no extrato BNB."
            )

        dates = [item.posted_at for item in transactions]
        return Statement(
            bank=BankInfo(code="004", name="Banco do Nordeste"),
            account=account,
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            opening_balance=opening_balance,
            closing_balance=last_balance,
            confidence=0.97,
            source_parser=self.key,
        )
