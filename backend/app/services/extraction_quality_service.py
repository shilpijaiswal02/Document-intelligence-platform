import re

from backend.app.schemas.extraction import (
    DocumentExtraction,
    Evidence,
    LineItem
)


def assess_extraction_quality(
    extracted_data: DocumentExtraction,
    ocr_text: str,
    document_type: str
) -> dict:
    warnings = []

    if not ocr_text.strip():
        warnings.append(
            "OCR text is empty."
        )

    if document_type == "invoice":
        has_item_keywords = any(
            keyword in ocr_text.upper()
            for keyword in [
                "ITEMS",
                "DESCRIPTION",
                "PRODUCT",
                "SERVICE",
                "NET PRICE",
                "NET WORTH",
                "GROSS WORTH"
            ]
        )

        if has_item_keywords and not extracted_data.line_items:
            warnings.append(
                "OCR contains possible invoice line items "
                "but no line items were extracted."
            )

    has_table_keywords = any(
        keyword in ocr_text.upper()
        for keyword in [
            "SUMMARY",
            "TOTAL",
            "NET PRICE",
            "NET WORTH",
            "BALANCE SHEET",
            "PROFIT",
            "CASH FLOW"
        ]
    )

    if has_table_keywords and not extracted_data.tables:
        warnings.append(
            "OCR contains possible tabular financial information "
            "but no tables were extracted."
        )

    return {
        "quality_status": (
            "WARNING"
            if warnings
            else "PASS"
        ),
        "warnings": warnings
    }


def recover_invoice_line_items(
    extracted_data: DocumentExtraction,
    ocr_text: str
) -> DocumentExtraction:

    # Do not overwrite Gemini's extracted line items.
    if extracted_data.line_items:
        return extracted_data

    lines = ocr_text.splitlines()

    recovered_items = []
    current_item = None
    inside_items_section = False

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Start of invoice items section.
        if line.upper() == "ITEMS":
            inside_items_section = True
            current_item = None
            continue

        # Stop when summary starts.
        if line.upper() == "SUMMARY":
            break

        if not inside_items_section:
            continue

        # Ignore table headers.
        if line.upper() in {
            "NO. DESCRIPTION QTY",
            "DESCRIPTION QTY"
        }:
            continue

        # An invoice item row should end with a quantity.
        quantity_match = re.search(
            r"(\d+[,.]\d*)$",
            line
        )

        if quantity_match:

            quantity_text = quantity_match.group(1)

            try:
                quantity = float(
                    quantity_text.replace(",", ".")
                )
            except ValueError:
                continue

            content = line[:quantity_match.start()].strip()

            # Try to extract a reliable item number.
            item_number_match = re.match(
                r"^(\d+)[\.\:\)]\s+(.+)$",
                content
            )

            if item_number_match:
                item_number = item_number_match.group(1)
                description = item_number_match.group(2).strip()
            else:
                # Item number was not reliably recognized by OCR.
                item_number = None
                description = content

            # Save previous item.
            if current_item:
                recovered_items.append(
                    LineItem(**current_item)
                )

            current_item = {
                "item_number": item_number,
                "description": description,
                "quantity": quantity
            }

            continue

        # Continuation of current item's description.
        if current_item:
            current_item["description"] += " " + line

    # Save final item.
    if current_item:
        recovered_items.append(
            LineItem(**current_item)
        )

    if recovered_items:
        extracted_data.line_items = recovered_items

    return extracted_data


def add_ocr_evidence(
    extracted_data: DocumentExtraction,
    ocr_text: str
) -> DocumentExtraction:

    # Do not duplicate evidence.
    if extracted_data.evidence:
        return extracted_data

    if not ocr_text.strip():
        return extracted_data

    extracted_data.evidence.append(
        Evidence(
            source_text=ocr_text[:2000],
            page_number=1
        )
    )

    return extracted_data