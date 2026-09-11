import json
import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.app.schemas.document import DocumentResponse
from backend.app.core.database import get_db
from backend.app.services.document_service import process_document


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
}


ALLOWED_DOCUMENT_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement"
}


@router.post(
    "/process",
    response_model=DocumentResponse
)
async def process_document_api(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db)
):
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_DOCUMENT_TYPE",
                "message": "Unsupported document type."
            }
        )

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "UNSUPPORTED_FILE_TYPE",
                "message": "Only PDF / JPG / PNG documents are supported."
            }
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            shutil.copyfileobj(
                file.file,
                temp_file
            )

            temp_path = temp_file.name

        document = process_document(
            db=db,
            file_path=temp_path,
            document_name=file.filename,
            document_type=document_type
        )

        return {
            "document_name": document.document_name,
            "document_type": document.document_type,
            "processing_status": document.processing_status,
            "file_validation": json.loads(
                document.file_validation
            ),
            "extracted_data": json.loads(
                document.extracted_data
            ),
            "validation": json.loads(
                document.validation
            ),
            "processing_metadata": json.loads(
                document.processing_metadata
            )
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "DOCUMENT_PROCESSING_ERROR",
                "message": str(exc)
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the document."
            }
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ⬇️ ADD FROM HERE


@router.get("")
def get_all_documents(
    db: Session = Depends(get_db)
):
    from backend.app.repositories.document_repository import (
        get_all_documents as repository_get_all_documents
    )

    documents = repository_get_all_documents(db)

    return [
        {
            "document_name": document.document_name,
            "document_type": document.document_type,
            "processing_status": document.processing_status,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get(
    "/{document_name}",
    response_model=DocumentResponse
)
def get_document(
    document_name: str,
    db: Session = Depends(get_db)
):
    from backend.app.repositories.document_repository import (
        get_latest_document
    )

    document = get_latest_document(
        db,
        document_name
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "DOCUMENT_NOT_FOUND",
                "message": "Document not found."
            }
        )

    return {
        "document_name": document.document_name,
        "document_type": document.document_type,
        "processing_status": document.processing_status,
        "file_validation": json.loads(
            document.file_validation
        ),
        "extracted_data": json.loads(
            document.extracted_data
        ),
        "validation": json.loads(
            document.validation
        ),
        "processing_metadata": json.loads(
            document.processing_metadata
        ),
        "created_at": document.created_at,
    }