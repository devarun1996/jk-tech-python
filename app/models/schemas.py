from pydantic import BaseModel

class IngestRequest(BaseModel):
    document_id: str
    content: str

class QuestionRequest(BaseModel):
    question: str