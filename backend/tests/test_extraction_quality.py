from backend.app.schemas.extraction import DocumentExtraction
from backend.app.services.extraction_quality_service import (
    assess_extraction_quality,
    add_ocr_evidence,
)


def test_detects_missing_invoice_line_items():
    extracted = DocumentExtraction(
        header={},
        dates=[],
        parties={},
        currency=None,
        totals={},
        line_items=[],
        comparative_periods=[],
        tables=[],
        additional_fields={},
        evidence=[]
    )

    ocr_text = """
    ITEMS
    No. Description Qty
    1. Product A 2
    2. Product B 3

    SUMMARY
    Net price Net worth VAT
    """

    result = assess_extraction_quality(
        extracted,
        ocr_text,
        "invoice"
    )

    assert result["quality_status"] == "WARNING"
    assert len(result["warnings"]) >= 1


def test_adds_ocr_evidence():
    extracted = DocumentExtraction(
        header={},
        dates=[],
        parties={},
        currency=None,
        totals={},
        line_items=[],
        comparative_periods=[],
        tables=[],
        additional_fields={},
        evidence=[]
    )

    result = add_ocr_evidence(
        extracted,
        "Invoice Number: INV-001"
    )

    assert len(result.evidence) == 1
    assert result.evidence[0].source_text == (
        "Invoice Number: INV-001"
    )
    assert result.evidence[0].page_number == 1