# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://snowpack_user:snowpack_dev_password@localhost:5432/snowpack_portal"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Keys (from your existing code)
    MESOWEST_TOKEN: str = ""  # Set this from your config
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Data directories
    DATA_DIR: str = "/app/data"
    CONFIG_DIR: str = "/app/config"
    SMET_DIR: str = "/app/data/smet"
    SNO_DIR: str = "/app/data/sno"
    RESULTS_DIR: str = "/app/data/results"
    
    # SNOWPACK settings
    SNOWPACK_EXECUTABLE: str = "snowpack"  # Path to SNOWPACK executable
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Scheduled task times (UTC)
    MORNING_RUN_HOUR: int = 4   # 4 AM
    EVENING_RUN_HOUR: int = 16  # 4 PM
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()