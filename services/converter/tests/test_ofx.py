from datetime import date
from decimal import Decimal

from pdf2ofx.domain.models import AccountInfo, BankInfo, Statement, Transaction
from pdf2ofx.exporters.ofx_102 import render_ofx


def test_ofx_102_is_cp1252_and_has_bank_data() -> None:
    statement = Statement(
        bank=BankInfo(code="341", name="Itaú"),
        account=AccountInfo(branch="7485", number="0001234-5"),
        transactions=[
            Transaction(
                posted_at=date(2026, 3, 2),
                description="PAGAMENTO À FORNECEDOR",
                amount=Decimal("-38.00"),
                transaction_type="DEBIT",
            )
        ],
        start_date=date(2026, 3, 2),
        end_date=date(2026, 3, 2),
        closing_balance=Decimal("100.00"),
    )
    output = render_ofx(statement)
    decoded = output.decode("cp1252")
    assert "OFXHEADER:100" in decoded
    assert "VERSION:102" in decoded
    assert "<BANKID>341" in decoded
    assert "<ORG>Itaú" in decoded
    assert "<FID>341" in decoded
    assert "<TRNAMT>-38.00" in decoded
    assert "PAGAMENTO À FORNECEDOR" in decoded
