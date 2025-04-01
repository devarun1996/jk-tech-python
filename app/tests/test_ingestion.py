import pytest
from pytest_mock import MockerFixture
import uuid
from sqlalchemy.orm import Session
from app.services.ingestion_service import ingest_document
from app.db import models
from datetime import datetime, timezone


@pytest.fixture
def sample_document(db: Session):
    """Creates a test document in the database"""
    doc = models.Document(id=uuid.uuid4(), 
                        document_source_id="sample_source_11",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc), 
                        content="Sample document", 
                        status=models.IngestionStatus.PENDING)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def test_ingest_document_success(db: Session, sample_document):
    """Test successful ingestion"""
    ingest_document(db, sample_document.id, "This is test content.")

    updated_doc = db.query(models.Document).filter(models.Document.id == sample_document.id).first()
    
    assert updated_doc is not None
    assert updated_doc.status == models.IngestionStatus.COMPLETED
    assert updated_doc.embedding is not None

    # Unpickle the embedding field and check if it's a list
    embedding = updated_doc.get_embedding()
    assert isinstance(embedding, list)

def test_ingest_document_not_found(db: Session):
    """Test when document does not exist"""
    with pytest.raises(ValueError, match="Document not found"):
        ingest_document(db, 999, "This document does not exist.")

def test_ingest_document_failure_handling(db: Session, sample_document, mocker: MockerFixture):
    """Test ingestion failure scenario"""
    mocker.patch("app.services.ingestion_service.embedding_model.encode", side_effect=Exception("Mocked error"))

    ingest_document(db, sample_document.id, "This will fail.")

    failed_doc = db.query(models.Document).filter(models.Document.id == sample_document.id).first()
    
    assert failed_doc.status == models.IngestionStatus.FAILED
