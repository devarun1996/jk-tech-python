from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document, SelectedDocument
from app.models.schemas import DocumentSelectionRequest, DocumentUnselectionRequest

router = APIRouter()

@router.post("/select-documents")
def select_documents(doc_select_request: DocumentSelectionRequest, db: Session = Depends(get_db)):
    user_id = doc_select_request.user_id
    document_source_ids = doc_select_request.document_ids

    # Fetch corresponding document IDs from the database
    documents = db.query(Document).filter(Document.document_source_id.in_(document_source_ids)).all()

    if not documents:
        raise HTTPException(status_code=404, detail="No matching documents found")
    
    # Map the found documents' IDs
    document_id_map = {doc.document_source_id: doc.id for doc in documents}

    selected_documents = []
    unmapped_documents = []

    for source_id in document_source_ids:
        if source_id in document_id_map:
            selected_documents.append(
                SelectedDocument(user_id=user_id, document_id=document_id_map[source_id])
            )
        else:
            unmapped_documents.append(source_id)

    if not selected_documents:
        raise HTTPException(status_code=400, detail="No valid document selections could be made")

    if selected_documents:
        db.add_all(selected_documents)
        db.commit()

    return {
        "message": "Document selection process completed",
        "total_requested": len(document_source_ids),
        "total_mapped": len(selected_documents),
        "total_unmapped": len(unmapped_documents),
        "unmapped_document_ids": unmapped_documents if unmapped_documents else None
    }


@router.get("/get-selected-documents/{user_id}")
def get_selected_documents(user_id: str, db: Session = Depends(get_db)):
    selected_docs = (
        db.query(SelectedDocument.document_id, Document.document_source_id)
        .join(Document, SelectedDocument.document_id == Document.id)
        .filter(SelectedDocument.user_id == user_id)
        .all()
    )

    # Convert query result into list of dictionaries
    result = [{"document_id": doc_id, "document_source_id": source_id} for doc_id, source_id in selected_docs]

    return {"selected_documents": result}


@router.delete("/unselect-document")
def unselect_document(removeDocumentRequest: DocumentUnselectionRequest, db: Session = Depends(get_db)):
    user_id = removeDocumentRequest.user_id
    document_source_id = removeDocumentRequest.document_id

    # Fetch the actual document ID from the database using document_source_id
    document = db.query(Document).filter(Document.document_source_id == document_source_id).first()

    if not document:
        return {
            "message": "Document not found for the given document_source_id",
            "document_source_id": document_source_id,
            "status": "failed"
        }

    # Delete the selection record if it exists
    deleted_rows = db.query(SelectedDocument).filter(
        SelectedDocument.user_id == user_id,
        SelectedDocument.document_id == document.id
    ).delete()

    db.commit()

    if deleted_rows == 0:
        return {
            "message": "No matching selection found for the user and document",
            "document_source_id": document_source_id,
            "status": "failed"
        }

    return {
        "message": "Document unselected successfully",
        "document_source_id": document_source_id,
        "status": "success"
    }


