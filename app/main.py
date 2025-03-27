from fastapi import FastAPI
from app.routes import ingestion, qa

app = FastAPI()

app.include_router(ingestion.router, prefix="/api")
app.include_router(qa.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "FastAPI Document Ingestion Service is Running!"}
