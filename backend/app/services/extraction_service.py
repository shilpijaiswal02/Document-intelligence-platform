import json

from google import genai

from backend.app.core.config import settings
from backend.app.schemas.extraction import DocumentExtraction


client = genai.Client(
    api_key=settings.gemini_api_key
)


EXTRACTION_PROMPT = """
You are a financial document extraction system.

Document type:
{document_type}

Extract ALL meaningful information present in the OCR text.

IMPORTANT RULES:

1. Never invent, guess, infer, or assume a value.

2. If a value is missing or unreadable, return null.

3. Preserve values from the document as accurately as possible.

4. Extract ALL meaningful visible information, not only a few
   important fields.

5. Extract headers, dates, parties, addresses, tax IDs, currencies,
   totals, line items, tables, bank details, comparative periods,
   and other meaningful fields.

6. If the document contains an ITEMS, DESCRIPTION, PRODUCTS,
   SERVICES, or similar table, extract EVERY visible row into
   line_items.

7. NEVER return an empty line_items array when visible invoice
   line items are present in the OCR text.

8. For EVERY visible invoice line item, extract:

   - item number if visible
   - description
   - HSN/SAC if visible
   - quantity
   - unit
   - rate/net price
   - discount if visible
   - line amount/net worth
   - tax rate
   - tax amount
   - gross amount

9. Preserve the relationship between description, quantity, rate,
   tax, discount, and amount for every line item.

10. If the OCR contains columns such as:

    Net price
    Net worth
    VAT
    Gross worth

    preserve those values for the corresponding line item.

11. If the document contains a summary or financial table,
    extract it into tables.

12. NEVER return an empty tables array when a meaningful financial
    table is present in the OCR text.

13. For every meaningful table, preserve:

    - table heading/name when visible
    - column headers
    - row labels
    - individual values
    - comparative period values

    Do not summarize a table when individual values are visible.

14. For financial statements, map clearly identifiable totals
    into the totals object.

15. Preserve other financial statement rows in tables.

16. Preserve comparative-year or comparative-period values in
    comparative_periods when they are present.

17. Extract currency symbols or currency names when visible.

18. Do not perform financial calculations yourself.

19. Financial validation will be performed separately by Python.

20. OCR text may contain errors. Do not silently invent corrections.

21. If an OCR value is uncertain, preserve the available text
    rather than replacing it with a guessed value.

22. Include supporting OCR text as evidence where practical.

23. Add evidence entries for important extracted values.

24. The evidence source_text should contain the supporting OCR
    text when practical.

25. Include page number when available.

26. Do not calculate missing values.

27. Do not infer values that are not explicitly present.

28. Return only the requested structured JSON.

For an invoice, pay particular attention to:

- invoice number
- invoice date
- seller
- buyer/client
- addresses
- tax IDs
- bank/payment information
- currency
- item number
- item description
- HSN/SAC
- quantity
- unit
- rate/net price
- discount
- line amount/net worth
- VAT/tax rate
- VAT/tax amount
- subtotal/net amount
- total tax
- gross/total amount
- amount in words

CRITICAL INVOICE RULE:

If the OCR contains something like:

ITEMS
No. Description Qty

1. Product A 2
2. Product B 3
3. Product C 5

then ALL visible items must appear as separate objects
inside line_items.

CRITICAL TABLE RULE:

If the OCR contains a table such as:

Net price | Net worth | VAT | Gross worth

preserve the individual values and their relationship
to the corresponding rows.

CRITICAL FINANCIAL STATEMENT RULE:

If the document contains multiple periods or comparative
years, preserve the values for EACH period separately.

CRITICAL EVIDENCE RULE:

Do not leave evidence empty when useful supporting OCR text
is available. Include source_text and page_number when
they can be determined from the input.

DOCUMENT TEXT:

{text}
"""


def extract_document(
    text: str,
    document_type: str
) -> DocumentExtraction:

    prompt = EXTRACTION_PROMPT.format(
        document_type=document_type,
        text=text
    )

    response_schema = DocumentExtraction.model_json_schema()

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": response_schema
        }
    )

    response_text = interaction.output_text.strip()

    try:
        data = json.loads(response_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    return DocumentExtraction.model_validate(data)