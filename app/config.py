# app/config.py
# Configuration management using environment variables

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database Configuration
    DATABASE_URL: str

    # Application Settings
    APP_NAME: str = "Intelligent EV Charging & Route Optimization System"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
