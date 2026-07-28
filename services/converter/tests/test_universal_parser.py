from pdf2ofx.domain.models import ExtractedDocument
from pdf2ofx.parsers.generic import GenericParser


def test_universal_parser_infers_sign_from_balance_delta() -> None:
    text = """
    EXTRATO CONTA CORRENTE
    Agência 0001 Conta 98765-4
    março/2026
    01/03/2026 SALDO ANTERIOR 100,00
    02/03/2026 AJUSTE OPERACIONAL 50,00 150,00
    03/03/2026 AJUSTE OPERACIONAL 20,00 130,00
    """
    document = ExtractedDocument(
        pages_text=[text],
        words=[],
        page_widths={1: 595.0},
        page_heights={1: 842.0},
    )

    statement = GenericParser().parse(document)

    assert str(statement.transactions[0].amount) == "50.00"
    assert str(statement.transactions[1].amount) == "-20.00"
    assert str(statement.closing_balance) == "130.00"


def test_universal_parser_accepts_parenthesized_debit() -> None:
    text = """
    EXTRATO
    01/04/2026 SALDO INICIAL 500,00
    02/04/2026 COMPRA CARTAO (125,90) 374,10
    """
    document = ExtractedDocument(
        pages_text=[text],
        words=[],
        page_widths={1: 595.0},
        page_heights={1: 842.0},
    )

    statement = GenericParser().parse(document)

    assert str(statement.transactions[0].amount) == "-125.90"
