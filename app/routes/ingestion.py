from fastapi import APIRouter, HTTPException
from app.models.schemas import IngestRequest
from app.services.ingestion_service import process_document, get_document_status

router = APIRouter()

@router.post("/ingest")
async def ingest_document(request: IngestRequest):
    return process_document(request)

@router.get("/status/{document_id}")
async def get_status(document_id: str):
    status = get_document_status(document_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"documentId": document_id, "status": status}
