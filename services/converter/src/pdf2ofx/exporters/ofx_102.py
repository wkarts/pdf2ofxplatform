from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pdf2ofx.domain.models import Statement, Transaction
from pdf2ofx.domain.normalization import create_fitid

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _safe(value: str | None) -> str:
    text = _CONTROL_CHARS.sub("", value or "")
    return text.replace("&", "E").replace("<", "(").replace(">", ")")


def _date(value: datetime | object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d%H%M%S")
    return value.strftime("%Y%m%d000000")


def _amount(value: Decimal) -> str:
    return f"{value:.2f}"


def _transaction_block(item: Transaction, ordinal: int) -> str:
    fitid = item.fitid or create_fitid(
        item.posted_at,
        item.amount,
        item.description,
        item.document_number,
        ordinal,
    )
    checknum = (
        f"<CHECKNUM>{_safe(item.document_number)}\n"
        if item.document_number
        else ""
    )
    return (
        "<STMTTRN>\n"
        f"<TRNTYPE>{item.transaction_type}\n"
        f"<DTPOSTED>{_date(item.posted_at)}\n"
        f"<TRNAMT>{_amount(item.amount)}\n"
        f"<FITID>{fitid}\n"
        f"{checknum}"
        f"<NAME>{_safe(item.description)[:120]}\n"
        f"<MEMO>{_safe(item.description)[:255]}\n"
        "</STMTTRN>\n"
    )


def render_ofx(statement: Statement) -> bytes:
    transactions = sorted(
        statement.active_transactions(),
        key=lambda item: (item.posted_at, item.fitid or ""),
    )
    if not transactions:
        raise ValueError("Não há transações ativas para gerar o OFX.")

    start = statement.start_date or transactions[0].posted_at
    end = statement.end_date or transactions[-1].posted_at
    ledger = (
        statement.closing_balance
        if statement.closing_balance is not None
        else sum((item.amount for item in transactions), Decimal("0"))
    )
    now = datetime.now()
    body = [
        "OFXHEADER:100\n",
        "DATA:OFXSGML\n",
        "VERSION:102\n",
        "SECURITY:NONE\n",
        "ENCODING:USASCII\n",
        "CHARSET:1252\n",
        "COMPRESSION:NONE\n",
        "OLDFILEUID:NONE\n",
        "NEWFILEUID:NONE\n\n",
        "<OFX>\n",
        "<SIGNONMSGSRSV1>\n<SONRS>\n",
        "<STATUS>\n<CODE>0\n<SEVERITY>INFO\n</STATUS>\n",
        f"<DTSERVER>{_date(now)}\n",
        "<LANGUAGE>POR\n",
        "<FI>\n",
        f"<ORG>{_safe(statement.bank.name)}\n",
        f"<FID>{statement.bank.code}\n",
        "</FI>\n",
        "</SONRS>\n</SIGNONMSGSRSV1>\n",
        "<BANKMSGSRSV1>\n<STMTTRNRS>\n",
        "<TRNUID>0\n",
        "<STATUS>\n<CODE>0\n<SEVERITY>INFO\n</STATUS>\n",
        "<STMTRS>\n",
        f"<CURDEF>{statement.account.currency}\n",
        "<BANKACCTFROM>\n",
        f"<BANKID>{statement.bank.code}\n",
        f"<BRANCHID>{_safe(statement.account.branch or '0000')}\n",
        f"<ACCTID>{_safe(statement.account.number or '000000')}\n",
        f"<ACCTTYPE>{statement.account.account_type}\n",
        "</BANKACCTFROM>\n",
        "<BANKTRANLIST>\n",
        f"<DTSTART>{_date(start)}\n",
        f"<DTEND>{_date(end)}\n",
    ]
    for ordinal, transaction in enumerate(transactions):
        body.append(_transaction_block(transaction, ordinal))
    body.extend(
        [
            "</BANKTRANLIST>\n",
            "<LEDGERBAL>\n",
            f"<BALAMT>{_amount(ledger)}\n",
            f"<DTASOF>{_date(end)}\n",
            "</LEDGERBAL>\n",
            "</STMTRS>\n</STMTTRNRS>\n</BANKMSGSRSV1>\n</OFX>\n",
        ]
    )
    return "".join(body).encode("cp1252", errors="replace")


def write_ofx(statement: Statement, path: Path) -> None:
    path.write_bytes(render_ofx(statement))
