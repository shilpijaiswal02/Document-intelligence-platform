from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from backend.app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_name = Column(
        String,
        index=True,
        nullable=False
    )

    document_type = Column(
        String,
        nullable=False
    )

    processing_status = Column(
        String,
        nullable=False
    )

    file_validation = Column(
        Text,
        nullable=False
    )

    extracted_data = Column(
        Text,
        nullable=False
    )

    validation = Column(
        Text,
        nullable=False
    )

    processing_metadata = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )