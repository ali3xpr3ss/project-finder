from typing import List, Optional, Dict, Any, Union
from pydantic import BaseSettings, AnyHttpUrl, AnyUrl, validator
import secrets
from functools import lru_cache
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project Finder"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "project_finder"
    DATABASE_URL: Optional[AnyUrl] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Rate Limiting
    RATE_LIMIT_TIMES: int = 5
    RATE_LIMIT_MINUTES: int = 5

    class Config:
        case_sensitive = True
        env_file = ".env"

class DevelopmentSettings(Settings):
    class Config:
        env_file = ".env.development"

class ProductionSettings(Settings):
    class Config:
        env_file = ".env.production"

    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["https://project-finder.com"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    RATE_LIMIT_TIMES: int = 3
    RATE_LIMIT_MINUTES: int = 5

@lru_cache()
def get_settings():
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()