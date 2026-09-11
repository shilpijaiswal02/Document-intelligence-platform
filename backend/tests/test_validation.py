from backend.app.services.financial_validation_service import (
    validate_financial_document
)


def test_invoice_line_total_passes():
    data = {
        "line_items": [
            {
                "quantity": 2,
                "rate": 50,
                "amount": 100
            }
        ],
        "totals": {
            "subtotal": 100,
            "total_tax_amount": 18,
            "total_amount": 118
        }
    }

    result = validate_financial_document(
        "invoice",
        data
    )

    assert result["status"] == "PASS"


def test_invoice_line_total_fails():
    data = {
        "line_items": [
            {
                "quantity": 2,
                "rate": 50,
                "amount": 150
            }
        ],
        "totals": {
            "subtotal": 150,
            "total_tax_amount": 27,
            "total_amount": 177
        }
    }

    result = validate_financial_document(
        "invoice",
        data
    )

    assert result["status"] == "FAILED"


def test_missing_values_are_not_applicable():
    data = {
        "line_items": [],
        "totals": {}
    }

    result = validate_financial_document(
        "invoice",
        data
    )

    assert all(
        check["status"] == "NOT_APPLICABLE"
        for check in result["checks"]
    )