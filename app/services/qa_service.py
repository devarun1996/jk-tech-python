import pickle
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Document, SelectedDocument
from app.services.embedding_service import generate_embedding
from transformers import pipeline


# Load the Hugging Face model pipeline (use a suitable LLM for Q&A)
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")


def get_answer(user_id: str, question: str, db: Session):
    
    # Find the most relevant document based on the user's question.
    best_doc = get_matching_document(user_id, question, db)  
    
    if not best_doc:
        return {"error": "No relevant documents found."}

    # Generate an answer using the LLM
    response = qa_pipeline(question=question, context=best_doc.content)

    return response["answer"]


def get_matching_document(user_id: str, question: str, db: Session):

    # Generate embedding for the question
    question_embedding = generate_embedding(question)
         
    # Fetch relevant documents from the database
    selected_doc_ids = db.query(SelectedDocument.document_id).filter(SelectedDocument.user_id == user_id).all()\
        if user_id else []
    
    # Extract document IDs
    selected_doc_ids = [doc_id[0] for doc_id in selected_doc_ids]

    # Query documents based on selected IDs
    documents = db.query(Document).filter(Document.id.in_(selected_doc_ids)).all()\
        if selected_doc_ids else db.query(Document).all()
    
    if not documents:
        return None

    # Compute similarity scores
    best_doc = None
    best_score = -1
    for doc in documents:
        doc_embedding = pickle.loads(doc.embedding)
        doc_embedding = np.array(doc_embedding, dtype=np.float32)

        similarity_score = cosine_similarity(question_embedding, doc_embedding)

        if similarity_score > best_score:
            best_score = similarity_score
            best_doc = doc

    if not best_doc:
        return None
    
    return best_doc


def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    # Ensure vec2 is unpickled if stored as bytes
    if isinstance(vec2, bytes):
        vec2 = pickle.loads(vec2)

    # Convert to NumPy arrays
    vec1 = np.array(vec1, dtype=np.float32)
    vec2 = np.array(vec2, dtype=np.float32)

    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0  # Avoid division by zero

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))