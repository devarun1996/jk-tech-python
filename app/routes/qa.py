from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import QuestionRequest
from app.services.qa_service import get_answer
from pydantic import BaseModel

router = APIRouter()

@router.post("/qa")
def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    answer = get_answer(request.question, db)

    if not answer:
        raise HTTPException(status_code=404, detail="No relevant answer found.")
    
    return { "answer": answer }

