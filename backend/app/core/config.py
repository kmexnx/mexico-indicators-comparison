from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Mexico Indicators"
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "postgresql://mexico_app:mexico_pass@postgres/mexico_indicators")
    DB_ECHO_LOG: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # JWT Secret
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mexico_indicators_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Data sources
    INEGI_API_KEY: Optional[str] = os.getenv("INEGI_API_KEY")
    DATOS_ABIERTOS_API_KEY: Optional[str] = os.getenv("DATOS_ABIERTOS_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
