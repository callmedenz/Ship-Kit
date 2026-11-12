from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="ShipKit api", version="1.0.0")

class HealthResponse(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
def read_root():
    return {"message": "Welcome to ShipKit."}