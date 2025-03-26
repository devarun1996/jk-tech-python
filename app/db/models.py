from sqlalchemy import Column, String, Text, Enum, DateTime, LargeBinary
from datetime import datetime, timezone
from app.db.database import Base
import enum

class IngestionStatus(str, enum.Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(IngestionStatus), default=IngestionStatus.PENDING)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    embedding = Column(LargeBinary, nullable=True)  # Stores serialized embeddings
