from backend.app.schemas.extraction import DocumentExtraction
from backend.app.services.extraction_quality_service import (
    recover_invoice_line_items,
)


def test_recovers_invoice_line_items():
    extracted = DocumentExtraction()

    ocr_text = """
    ITEMS
    No. Description Qty
    1. Shoeless Joe 5,00
    2. The Fifty Greatest Conspiracies 3,00
    3. The Story of a Soul 5,00
    SUMMARY
    """

    result = recover_invoice_line_items(
        extracted_data=extracted,
        ocr_text=ocr_text,
    )

    assert len(result.line_items) == 3

    assert result.line_items[0].item_number == "1"
    assert result.line_items[0].description == "Shoeless Joe"
    assert result.line_items[0].quantity == 5.0

    assert result.line_items[1].item_number == "2"
    assert result.line_items[1].quantity == 3.0

    assert result.line_items[2].item_number == "3"
    assert result.line_items[2].quantity == 5.0


def test_does_not_overwrite_existing_line_items():
    extracted = DocumentExtraction(
        line_items=[
            {
                "item_number": "1",
                "description": "Existing Item",
                "quantity": 2,
            }
        ]
    )

    ocr_text = """
    1. Another Item 5,00
    """

    result = recover_invoice_line_items(
        extracted_data=extracted,
        ocr_text=ocr_text,
    )

    assert len(result.line_items) == 1
    assert result.line_items[0].description == "Existing Item"