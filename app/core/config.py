"""
Application configuration settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "MCQ Test Platform"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite+aiosqlite:///./mcq_test_platform.db"
    test_database_url: str = "sqlite+aiosqlite:///./test_mcq_test_platform.db"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()