from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "postgresql://site52_user:site52_password@localhost/site52"
    
    # JWT
    SECRET_KEY: str = "your_jwt_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Сервер
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Site52"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 