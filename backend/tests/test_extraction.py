from pathlib import Path

from backend.app.services.ocr_service import extract_text


def test_extract_text_from_pdf(tmp_path):
    import pymupdf

    pdf_path = tmp_path / "sample.pdf"

    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (50, 50),
        "Invoice Number: INV-001"
    )

    document.save(pdf_path)
    document.close()

    text = extract_text(str(pdf_path))

    assert "Invoice Number" in text
    assert "INV-001" in text


def test_extraction_service_returns_document_extraction(monkeypatch):
    from backend.app.services import extraction_service
    from backend.app.schemas.extraction import DocumentExtraction

    class FakeOutput:
        output_text = """
        {
            "header": {
                "invoice_number": "INV-001"
            },
            "dates": [],
            "parties": {},
            "currency": "INR",
            "totals": {},
            "line_items": [],
            "comparative_periods": [],
            "tables": [],
            "additional_fields": {},
            "evidence": []
        }
        """

    class FakeClient:
        class interactions:

            @staticmethod
            def create(
                model,
                input,
                response_format=None
            ):
                return FakeOutput()

    monkeypatch.setattr(
        extraction_service,
        "client",
        FakeClient()
    )

    result = extraction_service.extract_document(
        "Invoice Number: INV-001",
        "invoice"
    )

    assert isinstance(
        result,
        DocumentExtraction
    )

    assert result.header["invoice_number"] == "INV-001"
    assert result.currency == "INR"