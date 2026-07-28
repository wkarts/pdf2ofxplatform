from __future__ import annotations

from typing import Any


def result_status(result: dict[str, Any]) -> str:
    reconciliation = result.get("reconciliation") or {}
    if not bool(reconciliation.get("balanced", False)):
        return "review_required"
    if reconciliation.get("duplicates"):
        return "review_required"
    if reconciliation.get("low_confidence_indexes"):
        return "review_required"
    if float(result.get("confidence", 1.0)) < 0.80:
        return "review_required"
    return "completed"
