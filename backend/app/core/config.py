import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger("ruhani")

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings class to manage environment variables"""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    ELEVEN_LABS_API_KEY: Optional[str] = os.getenv("ELEVEN_LABS_API_KEY")
    FETCH_AI_API_KEY: Optional[str] = os.getenv("FETCH_AI_API_KEY")
    CORAL_API_KEY: Optional[str] = os.getenv("CORAL_API_KEY")
    
    # Snowflake Configuration
    SNOWFLAKE_ACCOUNT: Optional[str] = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: Optional[str] = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_DATABASE: Optional[str] = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA: Optional[str] = os.getenv("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_WAREHOUSE: Optional[str] = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_ROLE: Optional[str] = os.getenv("SNOWFLAKE_ROLE")
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "default-secret-key-for-development-only")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Application Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Feature flags
    SEED_SAMPLE_DATA: bool = os.getenv("SEED_SAMPLE_DATA", "true").lower() == "true"
    
    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode"""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_required_settings(self) -> Dict[str, bool]:
        """Validate that all required settings are present"""
        validation_results = {}
        
        # Check Snowflake settings
        snowflake_settings = [
            "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA", "SNOWFLAKE_WAREHOUSE"
        ]
        
        for setting in snowflake_settings:
            value = getattr(self, setting)
            validation_results[setting] = value is not None and value != ""
            
        # Check API keys
        api_keys = ["GROQ_API_KEY", "ELEVEN_LABS_API_KEY", "FETCH_AI_API_KEY", "CORAL_API_KEY"]
        
        for key in api_keys:
            value = getattr(self, key)
            validation_results[key] = value is not None and value != ""
        
        # Log missing settings
        missing_settings = [k for k, v in validation_results.items() if not v]
        if missing_settings:
            logger.warning(f"Missing required settings: {', '.join(missing_settings)}")
        
        return validation_results


# Create a global settings instance
settings = Settings()