"""
Application configuration settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "MCQ Test Platform"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/mcq_test_db"
    test_database_url: str = "postgresql+asyncpg://user:password@localhost/mcq_test_db_test"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()