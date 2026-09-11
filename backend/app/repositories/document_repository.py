import json

from sqlalchemy.orm import Session

from backend.app.models.document import Document


def create_document(
    db: Session,
    document_name: str,
    document_type: str,
    processing_status: str,
    file_validation: dict,
    extracted_data: dict,
    validation: dict,
    processing_metadata: dict
):
    document = Document(
        document_name=document_name,
        document_type=document_type,
        processing_status=processing_status,
        file_validation=json.dumps(file_validation),
        extracted_data=json.dumps(extracted_data),
        validation=json.dumps(validation),
        processing_metadata=json.dumps(processing_metadata)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_latest_document(
    db: Session,
    document_name: str
):
    return (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .order_by(Document.created_at.desc())
        .first()
    )


def get_all_documents(db: Session):
    return (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )