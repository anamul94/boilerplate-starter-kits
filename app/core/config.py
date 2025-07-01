from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# Force reload of environment variables
load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL: Optional[str] = os.getenv("GOOGLE_DISCOVERY_URL")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Validate required settings
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")