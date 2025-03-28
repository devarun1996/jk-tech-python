from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SelectedDocument
from app.models.schemas import DocumentSelectionRequest, QuestionRequest
from app.services.qa_service import get_answer

router = APIRouter()

@router.post("/qa")
def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    user_id = request.user_id if request.user_id else None
    answer = get_answer(user_id, request.question, db)

    if not answer:
        raise HTTPException(status_code=404, detail="No relevant answer found.")
    
    return { "answer": answer }
