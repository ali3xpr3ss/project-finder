from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Matching API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
     # Token refresh lifetime
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, env="RATE_LIMIT_PER_MINUTE")

    DB_ECHO: bool = Field(False, env="DB_ECHO")

    # Server port
    PORT: int = Field(8000, env="PORT")

    # PostgreSQL
    POSTGRES_SERVER: str = Field(..., env='POSTGRES_SERVER')
    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field(..., env='POSTGRES_DB')
    POSTGRES_PORT: str = Field(..., env='POSTGRES_PORT')
    
    # Redis
    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    REDIS_DB: int = Field(0, env='REDIS_DB')
    
    # JWT
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(["*"], env="BACKEND_CORS_ORIGINS")
    
    # Database
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Cache
    CACHE_EXPIRE_MINUTES: int = 60
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Matching
    MIN_MATCH_SCORE: float = 0.5
    MAX_MATCHES: int = 10
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def assemble_db_connection(self) -> Dict[str, Any]:
        """
        Собирает параметры подключения к базе данных в словарь
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_SERVER,
            "port": self.POSTGRES_PORT,
        }

    def get_database_url(self) -> str:
        """
        Формирует URL для подключения к базе данных
        """
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings() 
print("BACKEND_CORS_ORIGINS from env:", os.getenv("BACKEND_CORS_ORIGINS"))
print("Parsed BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)