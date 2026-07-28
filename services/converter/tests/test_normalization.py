from decimal import Decimal

from pdf2ofx.domain.normalization import parse_br_money


def test_parse_brazilian_money() -> None:
    assert parse_br_money("1.234,56") == Decimal("1234.56")
    assert parse_br_money("1.234,56-") == Decimal("-1234.56")
    assert parse_br_money("-38,00") == Decimal("-38.00")
    assert parse_br_money("500,00+") == Decimal("500.00")
