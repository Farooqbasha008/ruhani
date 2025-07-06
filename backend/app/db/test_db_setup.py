import logging
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db.init_snowflake import init_db
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ruhani")

def test_db_setup():
    """Test the database setup and initialization"""
    logger.info("Testing database setup and initialization...")
    
    # Validate required settings
    validation_results = settings.validate_required_settings()
    missing_settings = [k for k, v in validation_results.items() if not v]
    
    if missing_settings:
        logger.error(f"Missing required settings: {', '.join(missing_settings)}")
        logger.error("Please check your .env file and ensure all required settings are provided.")
        return False
    
    # Initialize database
    logger.info("Initializing database...")
    if init_db():
        logger.info("Database initialization successful!")
        return True
    else:
        logger.error("Database initialization failed.")
        return False

if __name__ == "__main__":
    success = test_db_setup()
    if success:
        logger.info("Database setup test completed successfully.")
        sys.exit(0)
    else:
        logger.error("Database setup test failed.")
        sys.exit(1)