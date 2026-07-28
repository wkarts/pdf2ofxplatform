from pdf2ofx.domain.models import ExtractedDocument
from pdf2ofx.parsers.catalog import BANK_PROFILES, canonical_bank_key
from pdf2ofx.parsers.registry import ParserRegistry


def document_for(identifier: str) -> ExtractedDocument:
    text = f"""
    {identifier}
    Extrato de conta corrente
    Agência: 1234 Conta: 12345-6
    Período março/2026
    01/03/2026 SALDO ANTERIOR 1.000,00
    02/03/2026 PIX RECEBIDO CLIENTE 500,00+ 1.500,00
    03/03/2026 PAGAMENTO DE BOLETO 200,00- 1.300,00
    03/03/2026 SALDO FINAL 1.300,00
    """
    return ExtractedDocument(
        pages_text=[text],
        words=[],
        page_widths={1: 595.0},
        page_heights={1: 842.0},
    )


def test_requested_banks_are_registered() -> None:
    registry = ParserRegistry()
    expected = {
        "bb",
        "santander",
        "inter",
        "caixa",
        "bradesco",
        "bnb",
        "itau",
        "next",
        "nubank",
        "mercado_pago",
        "generic",
    }
    assert expected.issubset(registry.supported_keys)


def test_aliases_are_normalized() -> None:
    assert canonical_bank_key("nubanck") == "nubank"
    assert canonical_bank_key("mercadopago") == "mercado_pago"
    assert canonical_bank_key("banco_brasil") == "bb"


def test_profiled_banks_parse_standard_brazilian_statement() -> None:
    registry = ParserRegistry()
    calibrated = {"itau", "bnb", "santander"}
    profiles = [profile for profile in BANK_PROFILES if profile.key not in calibrated]

    for profile in profiles:
        document = document_for(profile.identifiers[0])
        parser = registry.select(document, profile.key)
        statement = parser.parse(document)

        assert statement.bank.code == profile.code
        assert statement.bank.name == profile.name
        assert statement.account.branch == "1234"
        assert statement.account.number == "12345-6"
        assert len(statement.transactions) == 2
        assert str(statement.transactions[0].amount) == "500.00"
        assert str(statement.transactions[1].amount) == "-200.00"
        assert str(statement.opening_balance) == "1000.00"
        assert str(statement.closing_balance) == "1300.00"


def test_auto_detection_uses_generic_for_unknown_bank_layout() -> None:
    document = ExtractedDocument(
        pages_text=[
            "BANCO REGIONAL EXEMPLO\n"
            "01/03/2026 PIX RECEBIDO 100,00+ 100,00\n"
            "02/03/2026 PAGAMENTO 25,00- 75,00"
        ],
        words=[],
        page_widths={1: 595.0},
        page_heights={1: 842.0},
        used_ocr=False,
    )

    parser = ParserRegistry().select(document, "auto")

    assert parser.key == "generic"
