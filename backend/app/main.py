
from fastapi import FastAPI

app = FastAPI(
    title="Medicall API",
    description="AI-powered voice receptionist for doctor appointments",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Medicall API",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "Medicall"
    }
