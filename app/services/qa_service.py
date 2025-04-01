import redis
import pickle
import json
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Document, SelectedDocument
from app.services.embedding_service import generate_embedding
from transformers import pipeline
from app.utils.config import redis_client


# Load the Hugging Face model pipeline (use a suitable LLM for Q&A)
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")


def process_question(user_id: str, question: str, db: Session, task_id: str):
    """
    Process the question asynchronously and store the result in Redis.
    """

    # Check if the answer is already cached
    cached_answer = redis_client.get(f"qa:{question}")
    if cached_answer:
        answer = json.loads(cached_answer)
    else:
        answer = get_answer(user_id, question, db)
        if not answer:
            answer = "No relevant answer found."

        # Store result in Redis (Cache for 1 hour)
        redis_client.setex(f"qa:{question}", 3600, json.dumps(answer))

    # Store task status in Redis
    redis_client.setex(f"task:{task_id}", 3600, json.dumps({"status": "completed", "answer": answer}))


def get_answer(user_id: str, question: str, db: Session):
    """
    Fetch the answer from Redis cache or generate it using the model.
    """

    # Check Redis cache first
    cached_answer = redis_client.get(f"qa:{user_id}:{question}")
    if cached_answer:
        return json.loads(cached_answer)

    # No cached answer, generate a new one
    best_doc = get_matching_document(user_id, question, db)
    if not best_doc:
        return None

    response = qa_pipeline(question=question, context=best_doc.content)
    if response["score"] < 0.1:
        return None

    return response["answer"]


def get_matching_document(user_id: str, question: str, db: Session):
    """
    Find the most relevant document based on question embedding similarity.
    """
    question_embedding = generate_embedding(question)

    selected_doc_ids = db.query(SelectedDocument.document_id).filter(SelectedDocument.user_id == user_id).all() if user_id else []
    selected_doc_ids = [doc_id[0] for doc_id in selected_doc_ids]

    documents = db.query(Document).filter(Document.id.in_(selected_doc_ids)).all() if selected_doc_ids else db.query(Document).all()
    if not documents:
        return None

    best_doc = None
    best_score = -1
    for doc in documents:
        doc_embedding = pickle.loads(doc.embedding)
        doc_embedding = np.array(doc_embedding, dtype=np.float32)

        similarity_score = cosine_similarity(question_embedding, doc_embedding)

        if similarity_score > best_score:
            best_score = similarity_score
            best_doc = doc

    return best_doc


def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    if isinstance(vec2, bytes):
        vec2 = pickle.loads(vec2)

    vec1 = np.array(vec1, dtype=np.float32)
    vec2 = np.array(vec2, dtype=np.float32)

    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0  

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
