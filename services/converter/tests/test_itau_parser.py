from pdf2ofx.domain.models import ExtractedDocument, PositionedWord
from pdf2ofx.parsers.itau import ItauParser


def line_words(page: int, top: float, parts: list[tuple[str, float]]) -> list[PositionedWord]:
    return [
        PositionedWord(
            page=page,
            text=text,
            x0=x0,
            top=top,
            x1=x0 + max(20, len(text) * 6),
            bottom=top + 12,
            confidence=0.9,
        )
        for text, x0 in parts
    ]


def test_itau_parser_ignores_balance_rows_and_recovers_dropped_date_digit() -> None:
    words = []
    words += line_words(
        1,
        20,
        [
            ("Itaú", 10),
            ("Agência", 300),
            ("7485", 360),
            ("Conta", 410),
            ("0001234-5", 460),
        ],
    )
    words += line_words(
        1,
        100,
        [("11/03/2026", 10), ("PIX", 120), ("ENVIADO", 160), ("-170,00", 680)],
    )
    words += line_words(
        1,
        120,
        [("1/03/2026", 10), ("BOLETO", 120), ("PAGO", 180), ("-382,64", 680)],
    )
    words += line_words(
        1,
        140,
        [
            ("11/03/2026", 10),
            ("SALDOTOTAL", 120),
            ("DISPONÍVEL", 260),
            ("DIA", 390),
            ("7.040,21", 760),
        ],
    )

    document = ExtractedDocument(
        pages_text=[
            "Itaú Agência 7485 Conta 0001234-5\n"
            "11/03/2026 PIX ENVIADO -170,00\n"
            "1/03/2026 BOLETO PAGO -382,64\n"
            "11/03/2026 SALDOTOTAL DISPONÍVEL DIA 7.040,21"
        ],
        words=words,
        page_widths={1: 900.0},
        page_heights={1: 1200.0},
        used_ocr=True,
    )

    statement = ItauParser().parse(document)

    assert statement.account.branch == "7485"
    assert statement.account.number == "0001234-5"
    assert len(statement.transactions) == 2
    assert statement.transactions[1].posted_at.day == 11
    assert str(statement.closing_balance) == "7040.21"
