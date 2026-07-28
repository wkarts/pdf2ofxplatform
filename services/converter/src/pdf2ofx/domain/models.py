from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class PositionedWord:
    page: int
    text: str
    x0: float
    top: float
    x1: float
    bottom: float
    confidence: float = 1.0


@dataclass(slots=True)
class ExtractedDocument:
    pages_text: list[str]
    words: list[PositionedWord]
    page_widths: dict[int, float]
    page_heights: dict[int, float]
    used_ocr: bool = False

    @property
    def text(self) -> str:
        return "\n".join(self.pages_text)


@dataclass(slots=True)
class BankInfo:
    code: str
    name: str


@dataclass(slots=True)
class AccountInfo:
    branch: str | None = None
    number: str | None = None
    account_type: str = "CHECKING"
    currency: str = "BRL"


@dataclass(slots=True)
class Transaction:
    posted_at: date
    description: str
    amount: Decimal
    document_number: str | None = None
    balance: Decimal | None = None
    transaction_type: str = "OTHER"
    source_page: int = 1
    confidence: float = 1.0
    fitid: str | None = None
    deleted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["posted_at"] = self.posted_at.isoformat()
        payload["amount"] = f"{self.amount:.2f}"
        payload["balance"] = (
            f"{self.balance:.2f}" if self.balance is not None else None
        )
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Transaction:
        return cls(
            posted_at=date.fromisoformat(str(payload["posted_at"])),
            description=str(payload["description"]),
            amount=Decimal(str(payload["amount"])),
            document_number=payload.get("document_number"),
            balance=(
                Decimal(str(payload["balance"]))
                if payload.get("balance") is not None
                else None
            ),
            transaction_type=str(payload.get("transaction_type", "OTHER")),
            source_page=int(payload.get("source_page", 1)),
            confidence=float(payload.get("confidence", 1.0)),
            fitid=payload.get("fitid"),
            deleted=bool(payload.get("deleted", False)),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(slots=True)
class Statement:
    bank: BankInfo
    account: AccountInfo
    transactions: list[Transaction]
    start_date: date | None = None
    end_date: date | None = None
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)
    source_parser: str = "unknown"

    def active_transactions(self) -> list[Transaction]:
        return [item for item in self.transactions if not item.deleted]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bank": asdict(self.bank),
            "account": asdict(self.account),
            "transactions": [item.to_dict() for item in self.transactions],
            "transaction_count": len(self.active_transactions()),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "opening_balance": (
                f"{self.opening_balance:.2f}"
                if self.opening_balance is not None
                else None
            ),
            "closing_balance": (
                f"{self.closing_balance:.2f}"
                if self.closing_balance is not None
                else None
            ),
            "confidence": self.confidence,
            "warnings": self.warnings,
            "source_parser": self.source_parser,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Statement:
        return cls(
            bank=BankInfo(**payload["bank"]),
            account=AccountInfo(**payload["account"]),
            transactions=[
                Transaction.from_dict(item) for item in payload["transactions"]
            ],
            start_date=(
                date.fromisoformat(payload["start_date"])
                if payload.get("start_date")
                else None
            ),
            end_date=(
                date.fromisoformat(payload["end_date"])
                if payload.get("end_date")
                else None
            ),
            opening_balance=(
                Decimal(str(payload["opening_balance"]))
                if payload.get("opening_balance") is not None
                else None
            ),
            closing_balance=(
                Decimal(str(payload["closing_balance"]))
                if payload.get("closing_balance") is not None
                else None
            ),
            confidence=float(payload.get("confidence", 1.0)),
            warnings=list(payload.get("warnings", [])),
            source_parser=str(payload.get("source_parser", "unknown")),
        )
