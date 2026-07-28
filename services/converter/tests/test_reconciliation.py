from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import AccountInfo, BankInfo, Statement, Transaction
from pdf2ofx.validation.reconciliation import reconcile


def test_reconciliation_balances_statement() -> None:
    statement = Statement(
        bank=BankInfo(code="004", name="Banco do Nordeste"),
        account=AccountInfo(),
        opening_balance=Decimal("100.00"),
        closing_balance=Decimal("130.00"),
        transactions=[
            Transaction(date(2026, 3, 1), "Crédito", Decimal("50.00")),
            Transaction(date(2026, 3, 1), "Débito", Decimal("-20.00")),
        ],
    )
    result = reconcile(statement)
    assert result["balanced"] is True
    assert result["calculated_closing"] == "130.00"


def test_reconciliation_is_partial_without_opening_balance() -> None:
    statement = Statement(
        bank=BankInfo(code="000", name="Banco"),
        account=AccountInfo(),
        transactions=[
            Transaction(date(2026, 3, 1), "Crédito", Decimal("50.00")),
        ],
        closing_balance=Decimal("50.00"),
    )
    result = reconcile(statement)
    assert result["balanced"] is False
    assert "saldo inicial" in str(result["warnings"][0]).lower()
