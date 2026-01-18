from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.
    Uses environment variables for configuration.
    """
    # Database
    DATABASE_URL: str = "postgresql://neurosupport:neurosupport123@localhost:5432/neurosupport_db"
    
    # Application
    APP_NAME: str = "NeuroSupport"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # AI Model
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    USE_FALLBACK_EMOTION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
