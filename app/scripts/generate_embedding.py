from sentence_transformers import SentenceTransformer
import os
import pickle

# Load embedding model
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
embedding_model = SentenceTransformer(MODEL_NAME)
content="Artificial Intelligence is the simulation of human intelligence in machines."

# Generate embeddings
embedding_list = embedding_model.encode(content).tolist()
final_embedding = pickle.dumps(embedding_list)

print(final_embedding)