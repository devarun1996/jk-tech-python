import time

# In-memory storage for document status
document_status = {}

def process_document(request):
    document_status[request.documentId] = "Processing"
    print(f"Received document {request.documentId} for ingestion.")
    
    # Simulate processing delay
    time.sleep(2)
    document_status[request.documentId] = "Completed"

    return {"message": "Ingestion started", "documentId": request.documentId}

def get_document_status(document_id: str):
    return document_status.get(document_id)
