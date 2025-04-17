import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api.routes.auth import (
    auth_router,
    users_router,
    projects_router,
    matching_router,
    notifications_router
)

app = FastAPI(
    title="Project Management API",
    description="""
    API для управления проектами и участниками.
    
    ## Возможности
    * 🔐 Аутентификация и авторизация пользователей
    * 👥 Управление профилями участников
    * 📋 Управление проектами
    * 🔍 Семантический поиск проектов и анкет
    * 🤝 Сопоставление проектов и участников
    * 🔔 Система уведомлений
    
    ## Основные эндпоинты
    * `/api/auth` - аутентификация и токены
    * `/api/users` - управление пользователями
    * `/api/projects` - управление проектами
    * `/api/matching` - сопоставление проектов и участников
    * `/api/notifications` - управление уведомлениями
    
    ## Технологии
    * FastAPI
    * SQLAlchemy
    * PostgreSQL
    * JWT
    * Sentence Transformers
    * FAISS
    * Redis
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
init_db()

# Подключаем роутеры
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(projects_router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(matching_router, prefix=f"{settings.API_V1_STR}/matching", tags=["matching"])
app.include_router(notifications_router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])

@app.get("/", tags=["info"])
async def root():
    """
    Корневой эндпоинт API.
    
    Возвращает приветственное сообщение и базовую информацию о API.
    """
    return {
        "message": "Welcome to Project Management API",
        "version": "1.0.0",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json"
    } 