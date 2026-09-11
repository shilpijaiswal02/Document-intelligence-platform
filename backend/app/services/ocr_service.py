import os
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


# Use TESSERACT_CMD when explicitly configured.
# Otherwise, let pytesseract find Tesseract from PATH.
tesseract_cmd = os.getenv("TESSERACT_CMD")

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
elif os.name == "nt":
    windows_tesseract = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if os.path.exists(windows_tesseract):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension in {".jpg", ".jpeg", ".png"}:
        return extract_image_text(file_path)

    raise ValueError("Unsupported file type")


def extract_pdf_text(file_path: str) -> str:
    document = pymupdf.open(file_path)
    text = []

    try:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text()

            if page_text.strip():
                text.append(page_text)
            else:
                # Render scanned PDF page as an image and run OCR.
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2)
                )

                image = Image.frombytes(
                    "RGB",
                    [pixmap.width, pixmap.height],
                    pixmap.samples,
                )

                ocr_text = pytesseract.image_to_string(image)
                text.append(ocr_text)

    finally:
        document.close()

    return "\n".join(text)


def extract_image_text(file_path: str) -> str:
    with Image.open(file_path) as image:
        return pytesseract.image_to_string(image)