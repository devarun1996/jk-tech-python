import pytest
import pickle
import os
from app.services.qa_service import get_answer
from app.db import models
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer

# Load embedding model
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
embedding_model = SentenceTransformer(MODEL_NAME)

@pytest.fixture
def sample_document(db: Session):
    """Creates a test document in the database"""
    content="Artificial Intelligence is the simulation of human intelligence in machines."
    embedding_list = embedding_model.encode(content).tolist()
    embedding = pickle.dumps(embedding_list)

    doc = models.Document(
        id=uuid.uuid4(), 
        document_source_id="sample_source_1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc), 
        embedding=embedding,
        content=content,
        status=models.IngestionStatus.PENDING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def test_get_answer_with_answer(db: Session, sample_document: models.Document):
    """Test when a valid answer is returned"""
    user_id = "test-user"
    question = "What is Artificial Intelligence?"

    # Ensure document is in selected documents for testing
    selected_doc = models.SelectedDocument(user_id=user_id, document_id=sample_document.id)
    db.add(selected_doc)
    db.commit()

    response = get_answer(user_id, question, db)
    
    # Assert the answer is returned as a string
    assert isinstance(response, str)
    assert len(response) > 0

def test_get_answer_no_best_doc_found(db: Session):
    """Test when no best document is found"""
    user_id = "test-user"
    question = "What is a non-existing concept?"

    response = get_answer(user_id, question, db)
    
    # Assert that no answer is returned
    assert response is None

def test_get_answer_low_score(db: Session, sample_document: models.Document):
    """Test when the answer generated from the best doc has a score below 0.1"""
    user_id = "test-user"
    question = "What is Artificial Intelligence?"

    # Simulate the scenario where the best document has a low score
    # Modify the embedding to simulate a bad match for this question
    sample_document.content = "This document is not relevant to AI."
    embedding_list = embedding_model.encode(sample_document.content).tolist()
    sample_document.embedding = pickle.dumps(embedding_list)
    db.commit()

    selected_doc = models.SelectedDocument(user_id=user_id, document_id=sample_document.id)
    db.add(selected_doc)
    db.commit()

    response = get_answer(user_id, question, db)
    
    # Assert that no answer is returned because the score is below 0.1
    assert response is None
