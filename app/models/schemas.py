from pydantic import BaseModel

class IngestRequest(BaseModel):
    document_id: str
    content: str

class QuestionRequest(BaseModel):
    question: str
    user_id: str

class DocumentSelectionRequest(BaseModel):
    user_id: str
    document_ids: list[str]

class DocumentUnselectionRequest(BaseModel):
    user_id: str
    document_id: str