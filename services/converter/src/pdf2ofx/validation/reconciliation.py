from __future__ import annotations

from decimal import Decimal

from pdf2ofx.domain.models import Statement


def _format_brl(value: Decimal) -> str:
    formatted = f"{abs(value):,.2f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def reconcile(statement: Statement) -> dict[str, object]:
    active = statement.active_transactions()
    total_credits = sum((item.amount for item in active if item.amount > 0), Decimal("0"))
    total_debits = sum((item.amount for item in active if item.amount < 0), Decimal("0"))
    calculated_closing: Decimal | None = None
    difference: Decimal | None = None
    balanced = False
    warnings: list[str] = []

    if statement.opening_balance is None:
        warnings.append("O saldo inicial não foi identificado; a conciliação ficou parcial.")
    else:
        calculated_closing = statement.opening_balance + total_credits + total_debits
        if statement.closing_balance is None:
            warnings.append("O saldo final não foi identificado; a conciliação ficou parcial.")
        else:
            difference = statement.closing_balance - calculated_closing
            balanced = abs(difference) <= Decimal("0.01")
            if not balanced:
                warnings.append(
                    "A soma das transações não fecha com o saldo final; "
                    f"diferença de R$ {_format_brl(difference)}."
                )

    seen: dict[tuple[str, str, str], int] = {}
    duplicates: list[dict[str, object]] = []
    for index, item in enumerate(active):
        key = (item.posted_at.isoformat(), f"{item.amount:.2f}", item.description.upper())
        if key in seen:
            duplicates.append({"first": seen[key], "duplicate": index})
        else:
            seen[key] = index
    if duplicates:
        warnings.append(
            f"Foram encontrados {len(duplicates)} possível(is) lançamento(s) duplicado(s)."
        )

    low_confidence = [
        index for index, item in enumerate(active) if item.confidence < 0.70
    ]
    if low_confidence:
        warnings.append(
            f"{len(low_confidence)} lançamento(s) possuem confiança inferior a 70%."
        )

    return {
        "balanced": balanced,
        "opening_balance": (
            f"{statement.opening_balance:.2f}"
            if statement.opening_balance is not None
            else None
        ),
        "total_credits": f"{total_credits:.2f}",
        "total_debits": f"{total_debits:.2f}",
        "calculated_closing": (
            f"{calculated_closing:.2f}" if calculated_closing is not None else None
        ),
        "reported_closing": (
            f"{statement.closing_balance:.2f}"
            if statement.closing_balance is not None
            else None
        ),
        "difference": f"{difference:.2f}" if difference is not None else None,
        "duplicates": duplicates,
        "low_confidence_indexes": low_confidence,
        "warnings": warnings,
    }
