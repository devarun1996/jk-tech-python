from sqlalchemy import Column, LargeBinary, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.db.database import Base

import enum

class IngestionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_source_id = Column(String, nullable=False, unique=True)  # NestJS document ID
    content = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)  # Stores serialized embeddings
    status = Column(Enum(IngestionStatus, name="ingestionstatus"), default=IngestionStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
