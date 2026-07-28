from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import (
    AccountInfo,
    BankInfo,
    ExtractedDocument,
    Statement,
    Transaction,
)
from pdf2ofx.domain.normalization import (
    DATE_RE,
    ISO_DATE_RE,
    MONEY_RE,
    classify_transaction,
    clean_text,
    create_fitid,
    infer_reference_month,
    infer_reference_year,
    normalize_ascii,
    parse_br_money,
    parse_date,
)
from pdf2ofx.parsers.catalog import BankProfile
from pdf2ofx.parsers.helpers import TextLine, group_words_into_lines

_ACCOUNT_PATTERNS = (
    re.compile(
        r"AG(?:E|Ê)NCIA\s*[:.-]?\s*(?P<branch>[0-9Xx.-]+).*?"
        r"CONTA(?:\s+CORRENTE)?\s*[:.-]?\s*(?P<account>[0-9Xx.-]+)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"CONTA(?:\s+CORRENTE)?\s*[:.-]?\s*(?P<account>[0-9Xx.-]+).*?"
        r"AG(?:E|Ê)NCIA\s*[:.-]?\s*(?P<branch>[0-9Xx.-]+)",
        re.IGNORECASE | re.DOTALL,
    ),
)
_DOCUMENT_AT_END = re.compile(r"(?P<document>[A-Z0-9*./-]{3,30})\s*$", re.IGNORECASE)

_BALANCE_MARKERS = (
    "SALDO ANTERIOR",
    "SALDO INICIAL",
    "SALDO FINAL",
    "SALDO ATUAL",
    "SALDO DISPONIVEL",
    "SALDO TOTAL",
    "SALDO DO DIA",
    "SALDO EM ",
    "SALDO DA CONTA",
    "SALDO CONTA CORRENTE",
)
_OPENING_MARKERS = ("SALDO ANTERIOR", "SALDO INICIAL")
_CLOSING_MARKERS = (
    "SALDO FINAL",
    "SALDO ATUAL",
    "SALDO DISPONIVEL",
    "SALDO TOTAL",
    "SALDO DO DIA",
    "SALDO EM ",
    "SALDO DA CONTA",
)
_SKIP_MARKERS = (
    "TOTAL DE CREDITOS",
    "TOTAL DE DEBITOS",
    "RESUMO DO PERIODO",
    "RESUMO -",
    "EXTRATO CONSOLIDADO",
    "CENTRAL DE ATENDIMENTO",
    "OUVIDORIA",
    "SAC ",
    "PAGINA:",
    "PAGINA ",
    "DATA DESCRICAO",
    "DATA HISTORICO",
    "LANCAMENTOS DO PERIODO",
    "MOVIMENTOS (R$)",
    "CREDITOS DEBITOS",
    "VALOR (R$)",
)
_POSITIVE_TERMS = (
    "CREDITO",
    "RECEB",
    "DEPOSITO",
    "RESGATE",
    "RENDIMENTO",
    "ESTORNO",
    "DEVOLUCAO",
    "CASHBACK",
    "ENTRADA",
    "TED RECEB",
    "PIX RECEB",
    "TRANSFERENCIA RECEB",
)
_NEGATIVE_TERMS = (
    "DEBITO",
    "PAGAMENTO",
    "PGTO",
    "PAGO",
    "COMPRA",
    "SAQUE",
    "TARIFA",
    "IOF",
    "JUROS",
    "ENCARGO",
    "APLICACAO",
    "PIX ENVIADO",
    "TED ENVIADA",
    "TRANSFERENCIA ENVIADA",
    "BOLETO",
    "TRIBUTO",
    "IMPOSTO",
)


@dataclass(slots=True)
class LogicalLine:
    page: int
    text: str
    confidence: float
    positioned: TextLine | None = None


@dataclass(slots=True)
class ParsedMoney:
    raw: str
    value: Decimal
    start: int
    end: int


class UniversalBrazilianParser:
    """Parser heurístico para layouts brasileiros com datas e valores monetários.

    O parser preserva revisão obrigatória quando não consegue confirmar saldos.
    Parsers calibrados continuam tendo prioridade no registro.
    """

    def __init__(self, profile: BankProfile | None = None) -> None:
        self.profile = profile

    def detect(self, document: ExtractedDocument) -> float:
        text = normalize_ascii(document.text)
        score = 0.0
        if self.profile:
            matches = sum(
                1
                for marker in self.profile.identifiers
                if normalize_ascii(marker) in text
            )
            if not matches:
                return 0.0
            score = min(0.92, 0.58 + (matches - 1) * 0.12)

        transaction_like = 0
        for line in document.text.splitlines():
            if (DATE_RE.search(line) or ISO_DATE_RE.search(line)) and MONEY_RE.search(line):
                transaction_like += 1
        score += min(0.25, transaction_like / 40)
        return min(score, 0.99)

    def parse(self, document: ExtractedDocument) -> Statement:
        year = infer_reference_year(document.text)
        month = infer_reference_month(document.text)
        account = self._extract_account(document.text)
        lines = self._logical_lines(document)
        credit_x, debit_x = self._detect_amount_columns(lines)

        transactions: list[Transaction] = []
        current_date: date | None = None
        opening_balance: Decimal | None = None
        closing_balance: Decimal | None = None
        last_known_balance: Decimal | None = None
        last_transaction: Transaction | None = None

        for logical_line in lines:
            line_text = clean_text(logical_line.text)
            if not line_text:
                continue
            normalized = normalize_ascii(line_text)
            compact = normalized.replace(" ", "")

            parsed_date = self._extract_date(line_text, year, month)
            if parsed_date:
                current_date = parsed_date

            monies = self._money_values(line_text)
            is_balance_line = any(marker in normalized for marker in _BALANCE_MARKERS)
            if is_balance_line and monies:
                balance_value = monies[-1].value
                if any(marker in normalized for marker in _OPENING_MARKERS):
                    opening_balance = balance_value
                    last_known_balance = balance_value
                elif any(marker in normalized for marker in _CLOSING_MARKERS):
                    closing_balance = balance_value
                    last_known_balance = balance_value
                continue

            if any(marker in normalized for marker in _SKIP_MARKERS):
                continue
            if not monies or current_date is None:
                if self._is_description_continuation(normalized, line_text, last_transaction):
                    continuation = self._description_continuation(line_text)
                    if continuation and continuation not in last_transaction.description:
                        last_transaction.description = clean_text(
                            f"{last_transaction.description} | {continuation}"
                        )
                continue

            amount_money, balance_money = self._select_amount_and_balance(monies)
            description, document_number = self._extract_description(
                line_text,
                amount_money,
                parsed_date,
            )
            if not description or self._looks_like_non_transaction(description, compact):
                continue

            reported_balance = balance_money.value if balance_money else None
            amount = self._resolve_sign(
                description=description,
                line_text=line_text,
                amount=amount_money,
                reported_balance=reported_balance,
                previous_balance=last_known_balance,
                logical_line=logical_line,
                credit_x=credit_x,
                debit_x=debit_x,
            )

            confidence = max(0.50, min(0.92, logical_line.confidence))
            if not self._has_explicit_direction(line_text, description):
                confidence = min(confidence, 0.78)
            if reported_balance is None:
                confidence = min(confidence, 0.82)

            transaction = Transaction(
                posted_at=current_date,
                description=description,
                amount=amount.quantize(Decimal("0.01")),
                document_number=document_number,
                balance=reported_balance,
                transaction_type=classify_transaction(description, amount),
                source_page=logical_line.page,
                confidence=confidence,
                metadata={
                    "parser_mode": "universal",
                    "raw_line": line_text[:1000],
                },
            )
            transaction.fitid = create_fitid(
                current_date,
                transaction.amount,
                description,
                document_number,
                len(transactions),
            )
            transactions.append(transaction)
            last_transaction = transaction

            if reported_balance is not None:
                if opening_balance is None and len(transactions) == 1:
                    opening_balance = reported_balance - transaction.amount
                last_known_balance = reported_balance
                closing_balance = reported_balance
            elif last_known_balance is not None:
                last_known_balance += transaction.amount

        if not transactions:
            bank_name = self.profile.name if self.profile else "não identificado"
            raise ValueError(
                f"Nenhuma movimentação foi identificada no extrato do banco {bank_name}. "
                "O layout pode exigir um parser calibrado com uma amostra real."
            )

        dates = [item.posted_at for item in transactions]
        average_confidence = sum(item.confidence for item in transactions) / len(transactions)
        bank = (
            BankInfo(code=self.profile.code, name=self.profile.name)
            if self.profile
            else BankInfo(code="000", name="Banco não identificado")
        )
        warnings = [
            "Layout interpretado pelo parser bancário universal; "
            "revise os lançamentos antes do uso."
        ]
        if self.profile is None:
            warnings.insert(0, "Banco não identificado automaticamente.")

        return Statement(
            bank=bank,
            account=account,
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            confidence=min(0.88, average_confidence),
            warnings=warnings,
            source_parser=self.profile.key if self.profile else "generic",
        )

    @staticmethod
    def _logical_lines(document: ExtractedDocument) -> list[LogicalLine]:
        if document.words:
            tolerance = 14.0 if document.used_ocr else 4.0
            return [
                LogicalLine(
                    page=line.page,
                    text=line.text,
                    confidence=line.confidence,
                    positioned=line,
                )
                for line in group_words_into_lines(document.words, tolerance=tolerance)
            ]

        result: list[LogicalLine] = []
        for page_number, page_text in enumerate(document.pages_text, start=1):
            for line in page_text.splitlines():
                result.append(
                    LogicalLine(
                        page=page_number,
                        text=clean_text(line),
                        confidence=0.76,
                    )
                )
        return result

    @staticmethod
    def _detect_amount_columns(lines: list[LogicalLine]) -> tuple[float | None, float | None]:
        credit_x: float | None = None
        debit_x: float | None = None
        for logical_line in lines:
            positioned = logical_line.positioned
            if positioned is None:
                continue
            for word in positioned.words:
                normalized = normalize_ascii(word.text)
                if normalized.startswith("CREDIT"):
                    credit_x = word.x0
                elif normalized.startswith("DEBIT"):
                    debit_x = word.x0
            if credit_x is not None and debit_x is not None:
                break
        return credit_x, debit_x

    @staticmethod
    def _extract_date(
        line_text: str,
        default_year: int,
        default_month: int | None,
    ) -> date | None:
        if not DATE_RE.search(line_text) and not ISO_DATE_RE.search(line_text):
            return None
        try:
            return parse_date(line_text, default_year, default_month)
        except ValueError:
            return None

    @staticmethod
    def _money_values(line_text: str) -> list[ParsedMoney]:
        values: list[ParsedMoney] = []
        for match in MONEY_RE.finditer(line_text):
            try:
                amount = parse_br_money(match.group(0))
            except ValueError:
                continue
            values.append(
                ParsedMoney(
                    raw=match.group(0),
                    value=amount,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return values

    @staticmethod
    def _select_amount_and_balance(
        monies: list[ParsedMoney],
    ) -> tuple[ParsedMoney, ParsedMoney | None]:
        if len(monies) == 1:
            return monies[0], None

        # Em extratos brasileiros, o último valor costuma ser o saldo e o
        # penúltimo o movimento.
        return monies[-2], monies[-1]

    @staticmethod
    def _extract_description(
        line_text: str,
        amount: ParsedMoney,
        parsed_date: date | None,
    ) -> tuple[str, str | None]:
        prefix = clean_text(line_text[: amount.start])
        prefix = ISO_DATE_RE.sub("", prefix, count=1)
        prefix = DATE_RE.sub("", prefix, count=1)
        prefix = clean_text(prefix.strip("|:- "))

        document_number: str | None = None
        match = _DOCUMENT_AT_END.search(prefix)
        if match:
            candidate = match.group("document")
            normalized = candidate.replace(".", "").replace("-", "").replace("/", "")
            if any(char.isdigit() for char in normalized) and len(normalized) >= 3:
                document_number = candidate
                prefix = clean_text(prefix[: match.start()].strip("|:- "))

        if parsed_date is not None and prefix == parsed_date.strftime("%d/%m/%Y"):
            prefix = ""
        return prefix, document_number

    @staticmethod
    def _looks_like_non_transaction(description: str, compact_line: str) -> bool:
        normalized = normalize_ascii(description)
        if normalized in {"CREDITOS", "DEBITOS", "MOVIMENTOS", "VALOR", "SALDO"}:
            return True
        if any(marker.replace(" ", "") in compact_line for marker in _SKIP_MARKERS):
            return True
        return len(description) < 2

    @staticmethod
    def _resolve_sign(
        *,
        description: str,
        line_text: str,
        amount: ParsedMoney,
        reported_balance: Decimal | None,
        previous_balance: Decimal | None,
        logical_line: LogicalLine,
        credit_x: float | None,
        debit_x: float | None,
    ) -> Decimal:
        raw = clean_text(amount.raw)
        if raw.startswith("-") or raw.endswith("-") or raw.startswith("("):
            return -abs(amount.value)
        if raw.startswith("+") or raw.endswith("+"):
            return abs(amount.value)

        following = normalize_ascii(line_text[amount.end : amount.end + 6])
        if re.search(r"\bD\b", following):
            return -abs(amount.value)
        if re.search(r"\bC\b", following):
            return abs(amount.value)

        positioned = logical_line.positioned
        if positioned is not None and (credit_x is not None or debit_x is not None):
            token = raw.replace(" ", "")
            amount_word = next(
                (
                    word
                    for word in positioned.words
                    if token in word.text.replace(" ", "")
                    or word.text.replace(" ", "") in token
                ),
                None,
            )
            if amount_word is not None:
                if debit_x is not None and amount_word.x0 >= debit_x - 8:
                    return -abs(amount.value)
                if credit_x is not None and amount_word.x0 >= credit_x - 8:
                    return abs(amount.value)

        if reported_balance is not None and previous_balance is not None:
            delta = reported_balance - previous_balance
            if abs(abs(delta) - abs(amount.value)) <= Decimal("0.02"):
                return delta

        normalized_description = normalize_ascii(description)
        positive = any(term in normalized_description for term in _POSITIVE_TERMS)
        negative = any(term in normalized_description for term in _NEGATIVE_TERMS)
        if positive and not negative:
            return abs(amount.value)
        return -abs(amount.value)

    @staticmethod
    def _has_explicit_direction(line_text: str, description: str) -> bool:
        raw = clean_text(line_text)
        if re.search(r"(?:^|\s)[+-]?\s*R?\$?\s*\d[\d.]*,\d{2}\s*[+-](?:\s|$)", raw):
            return True
        normalized = normalize_ascii(description)
        return any(term in normalized for term in (*_POSITIVE_TERMS, *_NEGATIVE_TERMS))

    @staticmethod
    def _is_description_continuation(
        normalized: str,
        line_text: str,
        last_transaction: Transaction | None,
    ) -> bool:
        if last_transaction is None or len(line_text) < 3:
            return False
        if any(marker in normalized for marker in (*_SKIP_MARKERS, *_BALANCE_MARKERS)):
            return False
        if DATE_RE.search(line_text) or ISO_DATE_RE.search(line_text) or MONEY_RE.search(line_text):
            return False
        return any(char.isalpha() for char in line_text)

    @staticmethod
    def _description_continuation(line_text: str) -> str:
        return clean_text(line_text.strip("|:- "))[:300]

    @staticmethod
    def _extract_account(text: str) -> AccountInfo:
        for pattern in _ACCOUNT_PATTERNS:
            match = pattern.search(text)
            if match:
                return AccountInfo(
                    branch=match.groupdict().get("branch"),
                    number=match.groupdict().get("account"),
                )
        account_only = re.search(
            r"CONTA(?:\s+CORRENTE)?\s*[:.-]?\s*(?P<account>[0-9Xx.-]{4,})",
            text,
            re.IGNORECASE,
        )
        return AccountInfo(number=account_only.group("account") if account_only else None)
