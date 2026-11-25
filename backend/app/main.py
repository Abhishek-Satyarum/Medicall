import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import doctors
from app.routes import doctors, availability
from app.routes import doctors, availability, appointments

app = FastAPI(
    title="Medicall API",
    description="AI-powered voice receptionist for doctor appointments",
    version="1.0.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctors.router, prefix="/api")
app.include_router(availability.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")

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