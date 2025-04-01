from transformers import AutoModel, AutoTokenizer
import torch
import os


# Load pre-trained embedding model
MODEL_NAME = os.getenv("PRE_TRAINED_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def generate_embedding(text: str):
    """
    Generates an embedding for the given text using a transformer model.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Use the mean of the last hidden states as the sentence embedding
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    
    return embedding
