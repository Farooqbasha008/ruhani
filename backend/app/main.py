from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.api import router as api_router
from app.core.tasks import process_session_with_ai
from app.api.deps import get_db
from app.models.session import WellnessSession

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RUHANI - Mental Wellness Platform API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    """Initialize services on startup"""
    # Could add database initialization here if needed
    pass

@app.get("/")
def root():
    return {"message": "Welcome to RUHANI Mental Wellness Platform"}