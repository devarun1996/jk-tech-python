import redis
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.qa_service import get_answer, process_question
from app.models.schemas import QuestionRequest
from app.utils.config import redis_client


router = APIRouter()

@router.post("/qa")
def ask_question(request: QuestionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user_id = request.user_id if request.user_id else None
    question = request.question
    task_id = str(uuid.uuid4())

    # Check Redis for existing answer
    cached_answer = redis_client.get(f"qa:{question}")
    if cached_answer:
        redis_client.set(f"task:{task_id}", json.dumps({"status": "completed", "answer": json.loads(cached_answer)}))
        return {"task_id": task_id, "answer": json.loads(cached_answer)}

    # Process the question asynchronously and store the answer in Redis
    background_tasks.add_task(process_question, user_id, question, db, task_id)

    return {"task_id": task_id, "status": "processing"}


@router.get("/qa/status/{task_id}")
def get_qa_status(task_id: str):

    # Check the status of an ongoing Q&A request.
    task_data = redis_client.get(f"task:{task_id}")

    if not task_data:
        return {"task_id": task_id, "status": "processing"}

    return json.loads(task_data)

