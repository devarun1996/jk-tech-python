import pickle
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Document
from app.services.embedding_service import generate_embedding
from transformers import pipeline


# Load the Hugging Face model pipeline (use a suitable LLM for Q&A)
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")


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


def get_answer(question: str, db: Session):
    
    # Find the most relevant document based on the user's question.
    best_doc = get_matching_document(question, db)  
    
    # Use the document content as context for LLM-based answer generation
    context = best_doc.content

    # Generate an answer using the LLM
    response = qa_pipeline(question=question, context=context)
    print('response................', response)
    
    return response["answer"]


def get_matching_document(question: str, db: Session):

    # Generate embedding for the question
    question_embedding = generate_embedding(question)

    # Fetch all documents from the database
    documents = db.query(Document).all()
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