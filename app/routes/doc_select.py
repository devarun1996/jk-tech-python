from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SelectedDocument
from app.models.schemas import DocumentSelectionRequest, DocumentUnselectionRequest

router = APIRouter()

@router.post("/select-documents")
def select_documents(doc_select_request: DocumentSelectionRequest, db: Session = Depends(get_db)):
    user_id = doc_select_request.user_id
    document_ids = doc_select_request.document_ids

    for doc_id in document_ids:
        selection = SelectedDocument(user_id=user_id, document_id=doc_id)
        db.add(selection)
    
    db.commit()
    return {"message": "Documents selected successfully"}


@router.get("/get-selected-documents/{user_id}")
def get_selected_documents(user_id: str, db: Session = Depends(get_db)):
    selected_docs = db.query(SelectedDocument.document_id).filter(SelectedDocument.user_id == user_id).all()
    
    return {"selected_documents": [doc_id[0] for doc_id in selected_docs]}


@router.delete("/unselect-document")
def unselect_document(removeDocumentRequest: DocumentUnselectionRequest, db: Session = Depends(get_db)):
    user_id = removeDocumentRequest.user_id
    document_id = removeDocumentRequest.document_id

    db.query(SelectedDocument).filter(
        SelectedDocument.user_id == user_id,
        SelectedDocument.document_id == document_id
    ).delete()
    
    db.commit()
    return {"message": "Document unselected successfully"}


