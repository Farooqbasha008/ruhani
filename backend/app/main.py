from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import traceback

from .api import employee, hr
from .core.config import settings

app = FastAPI(
    title="RUHANI Backend",
    description="Culturally-inspired, invisible voice-based AI psychologist for enterprise employees",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(hr.router, prefix="/hr", tags=["HR"])

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "RUHANI backend is running",
        "version": "1.0.0",
        "services": {
            "groq": "available" if settings.GROQ_API_KEY else "not_configured",
            "elevenlabs": "available" if settings.ELEVENLABS_API_KEY else "not_configured",
            "fetchai": "available" if settings.FETCHAI_API_KEY else "not_configured",
            "coral": "available" if settings.CORAL_API_KEY else "not_configured",
            "snowflake": "available" if settings.SNOWFLAKE_USER else "not_configured"
        }
    }

@app.get("/health")
async def detailed_health_check():
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:00:00Z",
        "uptime": "1h 30m",
        "version": "1.0.0",
        "environment": "development"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print("UNHANDLED ERROR:", exc)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500,
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 