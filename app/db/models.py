import pickle
from sqlalchemy import Column, ForeignKey, LargeBinary, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.db.database import Base

import enum

class IngestionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_source_id = Column(String, nullable=False, unique=True)  # NestJS document ID
    content = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)  # Stores serialized embeddings
    status = Column(Enum(IngestionStatus, name="ingestionstatus"), default=IngestionStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def set_embedding(self, embedding_list):
        """Convert list to binary before storing"""
        self.embedding = pickle.dumps(embedding_list)

    def get_embedding(self):
        """Convert binary back to list"""
        return pickle.loads(self.embedding) if self.embedding else None
    

class SelectedDocument(Base):
    __tablename__ = "selected_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), primary_key=True)