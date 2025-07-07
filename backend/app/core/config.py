import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RUHANI"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # AI Services
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_BASE_URL: str = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/v1")
    
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_API_BASE_URL: str = os.getenv("ELEVENLABS_API_BASE_URL", "https://api.elevenlabs.io/v1")
    
    FETCHAI_API_KEY: str = os.getenv("FETCHAI_API_KEY", "")
    FETCHAI_API_BASE_URL: str = os.getenv("FETCHAI_API_BASE_URL", "https://api.fetch.ai/v1")
    
    CORAL_API_KEY: str = os.getenv("CORAL_API_KEY", "")
    CORAL_API_BASE_URL: str = os.getenv("CORAL_API_BASE_URL", "https://api.coralprotocol.com/v1")
    
    # Database
    SNOWFLAKE_USER: str = os.getenv("SNOWFLAKE_USER", "")
    SNOWFLAKE_PASSWORD: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    SNOWFLAKE_ACCOUNT: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    SNOWFLAKE_WAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE", "")
    SNOWFLAKE_DATABASE: str = os.getenv("SNOWFLAKE_DATABASE", "")
    SNOWFLAKE_SCHEMA: str = os.getenv("SNOWFLAKE_SCHEMA", "")
    SNOWFLAKE_ROLE: str = os.getenv("SNOWFLAKE_ROLE", "")
    SNOWFLAKE_AUTHENTICATOR: str = os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake")
    
    # AI Configuration
    DEFAULT_AI_MODEL: str = "llama3-8b-8192"  # Groq model
    DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice ID
    SESSION_TIMEOUT: int = 300  # 5 minutes
    
    # Wellness Configuration
    MOOD_THRESHOLDS = {
        "critical": 1.5,
        "warning": 2.5,
        "stable": 3.5,
        "good": 4.5
    }

settings = Settings()

# Access config via os.getenv('KEY') 