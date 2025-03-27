from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.db import models

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def ingest_document(db: Session, document_id: int, content: str):
    # Fetch document entry
    document = db.query(models.Document).filter(models.Document.id == document_id).first()

    if not document:
        raise ValueError("Document not found")

    # Update status to processing
    document.status = models.IngestionStatus.PROCESSING
    db.commit()

    try:
        # Generate embeddings
        embedding_list = embedding_model.encode(content).tolist()

        # Update document with embeddings & status
        document.set_embedding(embedding_list)
        document.status = models.IngestionStatus.COMPLETED
    
    except Exception as e:
        document.status = models.IngestionStatus.FAILED
        print(f"Error during ingestion: {str(e)}")

    db.commit()
    db.refresh(document)
