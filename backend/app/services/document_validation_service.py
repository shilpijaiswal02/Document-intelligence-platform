from pathlib import Path

import pymupdf


SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def validate_document(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists() or path.stat().st_size == 0:
        return {
            "file_type": None,
            "is_supported": False,
            "is_readable": False,
            "page_count": None,
            "status": "FAILED",
            "error": "File is empty or does not exist."
        }

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return {
            "file_type": extension,
            "is_supported": False,
            "is_readable": False,
            "page_count": None,
            "status": "FAILED",
            "error": "Only PDF / JPG / PNG documents are supported."
        }

    if extension == ".pdf":
        try:
            document = pymupdf.open(file_path)
            page_count = len(document)
            document.close()

            if page_count == 0:
                return {
                    "file_type": "application/pdf",
                    "is_supported": True,
                    "is_readable": False,
                    "page_count": 0,
                    "status": "FAILED",
                    "error": "PDF contains no pages."
                }

            if page_count > 3:
                return {
                    "file_type": "application/pdf",
                    "is_supported": True,
                    "is_readable": True,
                    "page_count": page_count,
                    "status": "FAILED",
                    "error": "Documents must not exceed 3 pages."
                }

            return {
                "file_type": "application/pdf",
                "is_supported": True,
                "is_readable": True,
                "page_count": page_count,
                "status": "PASS"
            }

        except Exception:
            return {
                "file_type": "application/pdf",
                "is_supported": True,
                "is_readable": False,
                "page_count": None,
                "status": "FAILED",
                "error": "PDF is corrupted or unreadable."
            }

    # JPG / JPEG / PNG
    try:
        from PIL import Image

        with Image.open(file_path) as image:
            image.verify()

        return {
            "file_type": extension,
            "is_supported": True,
            "is_readable": True,
            "page_count": 1,
            "status": "PASS"
        }

    except Exception:
        return {
            "file_type": extension,
            "is_supported": True,
            "is_readable": False,
            "page_count": 1,
            "status": "FAILED",
            "error": "Image is corrupted or unreadable."
        }