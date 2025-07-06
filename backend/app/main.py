from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api import employee, hr
from .db.init_snowflake import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ruhani")

app = FastAPI(title="RUHANI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    if init_db():
        logger.info("Database initialization successful")
    else:
        logger.warning("Database initialization failed or partially succeeded")

app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(hr.router, prefix="/hr", tags=["HR"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RUHANI backend is running"}