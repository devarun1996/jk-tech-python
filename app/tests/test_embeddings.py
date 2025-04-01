import numpy as np
import pytest
from app.services.embedding_service import generate_embedding

def test_generate_embedding():
    text = "This is a test sentence."
    embedding = generate_embedding(text)
    
    # Check if the embedding is a numpy array
    assert isinstance(embedding, np.ndarray)
    assert len(embedding) > 0  # Ensure embeddings are generated
