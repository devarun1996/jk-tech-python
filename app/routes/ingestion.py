from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.models.schemas import IngestRequest
from app.db.models import IngestionStatus
from app.services.ingestion_service import ingest_document
from sqlalchemy import text

router = APIRouter()


@router.post("/ingest/")
def ingest_api(request: IngestRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Ensure the document ID is provided by NestJS
    if not request.document_id:
        raise HTTPException(status_code=400, detail="document_id is required")
    
    # Step 1: Query document from db else create document entry with pending status
    document = db.query(models.Document).filter(models.Document.document_source_id == request.document_id).first()

    if not document:
        new_document = models.Document(
            document_source_id=request.document_id,
            content=request.content,
            status=IngestionStatus.PENDING,  # Set status to pending initially
        )
        db.add(new_document)
    else:
        document.status = IngestionStatus.PENDING
        new_document = document
    
    db.commit()
    db.refresh(new_document)

    # Step 2: Start the ingestion process asynchronously
    background_tasks.add_task(ingest_document, db, new_document.id, request.content)

    return {"document_id": new_document.document_source_id, "status": new_document.status}


# API to check the ingestion status of a document.
@router.get("/ingest/status/{document_source_id}")
def check_ingestion_status(document_source_id: str, db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.document_source_id == document_source_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document_id": document.document_source_id, "status": document.status}
