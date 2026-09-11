import time
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.repositories.document_repository import create_document
from backend.app.services.document_validation_service import validate_document
from backend.app.services.ocr_service import extract_text
from backend.app.services.extraction_service import extract_document
from backend.app.services.extraction_quality_service import (
    assess_extraction_quality,
    add_ocr_evidence,
    recover_invoice_line_items,
)
from backend.app.services.financial_validation_service import (
    validate_financial_document,
)


def process_document(
    db: Session,
    file_path: str,
    document_name: str,
    document_type: str,
):
    start_time = time.time()

    # 1. Validate file
    file_validation = validate_document(file_path)

    if file_validation["status"] == "FAILED":
        raise ValueError(file_validation["error"])

    # 2. Extract OCR / PDF text
    text = extract_text(file_path)

    if not text.strip():
        raise ValueError("No readable text found in document.")

    # 3. AI extraction
    extracted_result = extract_document(
        text=text,
        document_type=document_type,
    )
    extracted_result = recover_invoice_line_items(
      extracted_data=extracted_result,
       ocr_text=text,
       )
    # 4. Add source evidence from OCR text
    extracted_result = add_ocr_evidence(
        extracted_data=extracted_result,
        ocr_text=text,
    )

    # 5. Assess extraction quality
    quality_result = assess_extraction_quality(
        extracted_data=extracted_result,
        ocr_text=text,
        document_type=document_type,
    )

    # 6. Convert extracted result to JSON-compatible dictionary
    extracted_data = extracted_result.model_dump()

    # 7. Financial validation
    validation = validate_financial_document(
        document_type,
        extracted_data,
    )

    # 8. Add extraction quality information
    validation["extraction_quality"] = quality_result

    processing_time = round(time.time() - start_time, 2)

    # 9. Processing metadata
    processing_metadata = {
        "processing_time_seconds": processing_time,
        "file_name": Path(file_path).name,
        "extraction_quality_status": quality_result["quality_status"],
    }

    # 10. Store result in database
    document = create_document(
        db=db,
        document_name=document_name,
        document_type=document_type,
        processing_status=validation["status"],
        file_validation=file_validation,
        extracted_data=extracted_data,
        validation=validation,
        processing_metadata=processing_metadata,
    )

    return document