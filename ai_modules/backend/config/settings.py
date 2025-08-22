from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Hiring Assistant"
    DEBUG: bool = False
    
    # AI 모델 설정
    GEMINI_API_KEY: str
    MODEL_NAME: str = "gemini-pro"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = None
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()