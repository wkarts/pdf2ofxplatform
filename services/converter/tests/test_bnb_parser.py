from pdf2ofx.domain.models import ExtractedDocument
from pdf2ofx.parsers.bnb import BnbParser


def test_bnb_parser_reads_day_inheritance_and_signs() -> None:
    text = """
    Banco do Nordeste
    Mês: Março/2026
    AGENCIA: 126 CONTA 12.345-6 - EMPRESA
    > DEMONSTRATIVO DA MOVIMENTACAO DE CONTA CORRENTE
    DIA HISTORICO DOCUMENTO VALOR SALDO
    SALDO ANTERIOR 0,00 139,47
    2 RECEBIMENTO VIA PIX 11971 673,02+ 812,49
    RECEBIMENTO VIA PIX 11971 700,00+ 1.512,49
    CHEQUE COMPENSADO 310 1.234,00- 278,49
    > RELACAO DE CHEQUES EM ORDEM NUMERICA DEBITADOS
    """
    document = ExtractedDocument(
        pages_text=[text],
        words=[],
        page_widths={1: 841.9},
        page_heights={1: 595.0},
    )
    statement = BnbParser().parse(document)
    assert statement.bank.code == "004"
    assert statement.account.branch == "126"
    assert statement.account.number == "12.345-6"
    assert len(statement.transactions) == 3
    assert str(statement.transactions[0].amount) == "673.02"
    assert str(statement.transactions[2].amount) == "-1234.00"
    assert statement.transactions[1].posted_at.day == 2
