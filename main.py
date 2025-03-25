from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI Document Ingestion Service is Running!"}
