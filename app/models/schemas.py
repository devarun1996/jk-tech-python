from pydantic import BaseModel

class IngestRequest(BaseModel):
    documentId: str
    content: str
