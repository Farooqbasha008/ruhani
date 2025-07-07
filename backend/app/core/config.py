from pydantic_settings import BaseSettings  # Changed from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "RUHANI - Mental Wellness Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ruhani.db")

    # API Settings
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # Coral Protocol (Privacy logging)
    CORAL_API_KEY: Optional[str] = os.getenv("CORAL_API_KEY")

    # Snowflake (Analytics)
    SNOWFLAKE_ACCOUNT: Optional[str] = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: Optional[str] = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE: str = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA: str = os.getenv("SNOWFLAKE_SCHEMA")

    class Config:
        env_file = ".env"

settings = Settings()