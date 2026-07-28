from pdf2ofx.application.status import result_status


def test_result_status_requires_review_for_unbalanced_statement() -> None:
    assert result_status({
        "confidence": 0.95,
        "reconciliation": {
            "balanced": False,
            "duplicates": [],
            "low_confidence_indexes": [],
        },
    }) == "review_required"


def test_result_status_completes_clean_statement() -> None:
    assert result_status({
        "confidence": 0.95,
        "reconciliation": {
            "balanced": True,
            "duplicates": [],
            "low_confidence_indexes": [],
        },
    }) == "completed"
