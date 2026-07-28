from __future__ import annotations

import re
from calendar import monthrange
from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import (
    AccountInfo,
    BankInfo,
    ExtractedDocument,
    PositionedWord,
    Statement,
    Transaction,
)
from pdf2ofx.domain.normalization import (
    MONEY_RE,
    classify_transaction,
    clean_text,
    create_fitid,
    infer_reference_year,
    normalize_ascii,
    parse_br_money,
)
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.helpers import TextLine, group_words_into_lines

_FULL_DATE = re.compile(r"^(\d{1,2})/(\d{2})/(\d{4})$")
_DATE_IN_LINE = re.compile(r"\b\d{1,2}/\d{2}/20\d{2}\b")
_ACCOUNT_RE = re.compile(
    r"AGENCIA\s*(?P<branch>\d+)\s+CONTA\s*(?P<account>[\d-]+)",
    re.IGNORECASE,
)
_NON_TRANSACTION_MARKERS = (
    "SALDOTOTALDISPONIVEL",
    "SALDOMOVIMENTACAO",
    "SALDOAPLIC",
    "SALDOANTERIOR",
    "DATALANCAMENTOS",
    "LANCAMENTOSDOPERIODO",
)
_POSITIVE_MARKERS = (
    "RECEBIDO",
    "RECEBIMENTO",
    "RENDIMENTOS",
    "RENDIMENTO",
    "RESAPLIC",
    "CREDITO",
    "DEPOSITO",
)


class ItauParser(StatementParser):
    key = "itau"
    name = "Itaú"

    def detect(self, document: ExtractedDocument) -> float:
        text = normalize_ascii(document.text)
        compact = re.sub(r"\s+", "", text)
        score = 0.0
        if "ITAU" in text:
            score += 0.65
        if "SALDOTOTALDISPONIVELDIA" in compact:
            score += 0.2
        if "APLAPLICAUTMAIS" in compact or "RESAPLICAUTMAIS" in compact:
            score += 0.15
        return min(score, 1.0)

    @staticmethod
    def _signed_amount(description: str, raw: str) -> Decimal:
        amount = parse_br_money(raw)
        if raw.strip().startswith(("-", "+")) or raw.strip().endswith(("-", "+")):
            return amount
        compact = re.sub(r"\s+", "", normalize_ascii(description))
        return amount if any(marker in compact for marker in _POSITIVE_MARKERS) else -amount

    @staticmethod
    def _resolve_date(raw: str, previous: date | None, fallback_year: int) -> date | None:
        match = _FULL_DATE.fullmatch(raw)
        if not match:
            return None
        day_text, month_text, year_text = match.groups()
        day = int(day_text)
        month = int(month_text)
        year = int(year_text) if year_text else fallback_year

        # Tesseract occasionally drops the first digit from 10-19 or 20-29.
        # When the prior line already established the day, recover the closest
        # non-decreasing candidate with the same final digit.
        if len(day_text) == 1 and previous and previous.year == year and previous.month == month:
            limit = monthrange(year, month)[1]
            candidates = [
                candidate
                for candidate in (day, day + 10, day + 20, day + 30)
                if candidate <= limit
            ]
            matching = [candidate for candidate in candidates if candidate >= previous.day]
            if matching:
                day = min(matching, key=lambda candidate: candidate - previous.day)

        try:
            return date(year, month, day)
        except ValueError:
            return None

    @staticmethod
    def _date_word(line: TextLine) -> str | None:
        for word in line.words:
            if _FULL_DATE.fullmatch(word.text):
                return word.text
        match = _DATE_IN_LINE.search(line.text)
        return match.group(0) if match else None

    @staticmethod
    def _transaction_amount(line: TextLine, date_word: str) -> tuple[str, int] | None:
        # Prefer the right-most strict monetary token. CNPJ/CPF values are not
        # matched by MONEY_RE and therefore do not interfere with this choice.
        matches = list(MONEY_RE.finditer(line.text))
        if not matches:
            return None
        match = matches[-1]
        return match.group(0), match.start()

    def parse(self, document: ExtractedDocument) -> Statement:
        text = normalize_ascii(document.text)
        account_match = _ACCOUNT_RE.search(text)
        account = AccountInfo(
            branch=account_match.group("branch") if account_match else None,
            number=account_match.group("account") if account_match else None,
        )
        transactions: list[Transaction] = []
        opening_balance: Decimal | None = None
        closing_balance: Decimal | None = None
        year = infer_reference_year(document.text)
        previous_date: date | None = None

        for line in group_words_into_lines(
            document.words,
            tolerance=16.0 if document.used_ocr else 4.0,
        ):
            line_text = line.text
            normalized = normalize_ascii(line_text)
            compact = re.sub(r"\s+", "", normalized)
            if not line_text:
                continue

            date_word = self._date_word(line)
            if not date_word:
                continue
            posted_at = self._resolve_date(date_word, previous_date, year)
            if posted_at is None:
                continue
            previous_date = posted_at

            amount_data = self._transaction_amount(line, date_word)
            if not amount_data:
                continue
            raw_amount, amount_start = amount_data

            if any(marker in compact for marker in _NON_TRANSACTION_MARKERS):
                value = parse_br_money(raw_amount)
                if "SALDOANTERIOR" in compact:
                    opening_balance = value
                elif "SALDOTOTALDISPONIVEL" in compact:
                    closing_balance = value
                continue

            before_amount = clean_text(line_text[:amount_start])
            description = clean_text(before_amount.replace(date_word, "", 1))
            description = re.sub(
                r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b|"
                r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
                "",
                description,
            )
            description = clean_text(description.strip("| -"))
            if not description:
                continue

            amount = self._signed_amount(description, raw_amount)
            confidence_words: list[PositionedWord] = [
                word for word in line.words if word.text in raw_amount or raw_amount in word.text
            ]
            amount_confidence = (
                sum(word.confidence for word in confidence_words) / len(confidence_words)
                if confidence_words
                else line.confidence
            )
            confidence = min(line.confidence, amount_confidence)
            transaction = Transaction(
                posted_at=posted_at,
                description=description,
                amount=amount,
                balance=None,
                transaction_type=classify_transaction(description, amount),
                source_page=line.page,
                confidence=max(0.45, confidence),
            )
            transaction.fitid = create_fitid(
                posted_at, amount, description, None, len(transactions)
            )
            transactions.append(transaction)

        if not transactions:
            raise ValueError(
                "Nenhuma movimentação foi identificada no extrato Itaú. "
                "Verifique a qualidade do PDF ou selecione o banco manualmente."
            )

        dates = [item.posted_at for item in transactions]
        confidence = sum(item.confidence for item in transactions) / len(transactions)
        return Statement(
            bank=BankInfo(code="341", name="Itaú"),
            account=account,
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            confidence=min(0.96, confidence),
            warnings=(
                ["O extrato exigiu OCR; revise lançamentos com baixa confiança."]
                if document.used_ocr
                else []
            ),
            source_parser=self.key,
        )
