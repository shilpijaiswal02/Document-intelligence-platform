from typing import Any

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    file_validation: dict[str, Any]
    extracted_data: dict[str, Any]
    validation: dict[str, Any]
    processing_metadata: dict[str, Any]