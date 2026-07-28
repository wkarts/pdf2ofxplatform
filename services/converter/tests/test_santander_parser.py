from pdf2ofx.domain.models import ExtractedDocument, PositionedWord
from pdf2ofx.parsers.santander import SantanderParser


def word(text: str, x0: float, top: float, x1: float | None = None) -> PositionedWord:
    return PositionedWord(
        page=1,
        text=text,
        x0=x0,
        top=top,
        x1=x1 or x0 + 25,
        bottom=top + 8,
    )


def test_santander_parser_uses_credit_and_debit_columns() -> None:
    words = [
        word("Santander", 20, 10),
        word("EXTRATO", 20, 20),
        word("CONSOLIDADO", 70, 20),
        word("INTELIGENTE", 140, 20),
        word("02/03", 34, 100),
        word("PIX", 65, 100),
        word("RECEBIDO", 82, 100),
        word("5.000,00", 379, 100),
        word("PAGAMENTO", 65, 120),
        word("DE", 110, 120),
        word("BOLETO", 125, 120),
        word("949,06-", 433, 120),
        word("COMPANHIA", 65, 130),
        word("BRASILEIRA", 115, 130),
    ]
    document = ExtractedDocument(
        pages_text=["Santander Empresas\nEXTRATO CONSOLIDADO INTELIGENTE\nmarço/2026"],
        words=words,
        page_widths={1: 595.3},
        page_heights={1: 841.9},
    )
    statement = SantanderParser().parse(document)
    assert len(statement.transactions) == 2
    assert str(statement.transactions[0].amount) == "5000.00"
    assert str(statement.transactions[1].amount) == "-949.06"
    assert "COMPANHIA BRASILEIRA" in statement.transactions[1].description
