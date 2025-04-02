# FastAPI Project Documentation

## 1. Project Overview

### Brief Summary
This FastAPI-based backend provides document ingestion and Q&A processing using embeddings. It integrates with the NestJS service for seamless data exchange
 and operates efficiently with PostgreSQL and Redis.

### Key Features
- Document Ingestion with Embeddings
- Q&A Processing using RAG
- Integration with NestJS Service
- Asynchronous API Handling

## 2. Installation & Setup

### Prerequisites
- Python (>=3.9 recommended)
- PostgreSQL Database
- Redis for caching
- Pretrained Transformer Model for Embeddings

### Clone the Repository
```sh
git clone <repository-url>
cd jk-tech-python
```

### Environment Variables
Create a `.env` file in the project root and configure the following:
```env
DATABASE_URL=

LLM_MODEL=deepset/roberta-base-squad2
PRE_TRAINED_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_MODEL=all-MiniLM-L6-v2

REDIS_HOST=
REDIS_PORT=
```

### Activate Virtual Environment
```sh
source venv/bin/activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Run Database Migrations
```sh
alembic upgrade head
```

### Run the Application Locally
```sh
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

## 3. API Documentation
The API is documented using FastAPI’s built-in OpenAPI documentation. Once the service is running, access the API documentation at:
```
http://localhost:5000/docs
```

## 4. Module Breakdown

### Document Ingestion
- Accepts document and processes embeddings in background using a model.
- Stores embeddings in the database for retrieval.

### Q&A Processing
- Accepts a question api request from nestjs
- Returns an answer if already exists in the cache or else returns taskId for the asynchronous processing.
- Retrieves relevant document embeddings.
- Generates responses using the RAG approach & LLM model.
- Saves the answer in redis against taskId and sets the status to complete.

### Integration with NestJS Service
- Listens for ingestion requests from NestJS.
- Responds to Q&A queries via API.
- Provides a polling like feature via taskId status check API.

## 5. Testing

- Running All Tests with Coverage
```sh
pytest --cov=app app/tests/
```

- Running a Specific Test Module
```sh
pytest app/tests/test_qa.py
pytest app/tests/test_ingestion.py
pytest app/tests/test_embeddings.py
```

## 6. Scripts

- Generate embeddings using a script
  1. Paste the sample content inside the app/scripts/generate_embedding.py file
  2. Run the below script:
  ```sh
  python app/scripts/generate_embedding.py
  ```
  3. Embedding is logged in the console.

