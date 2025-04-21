from typing import Generator, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Создаем базовый класс для моделей
Base = declarative_base()

engine = None

def get_engine() -> Any:
    """
    Получение экземпляра движка базы данных
    """
    global engine
    if engine is None:
        try:
            engine = create_engine(
                settings.get_database_url(),
                pool_pre_ping=True,
                echo=settings.DB_ECHO
            )
            logger.info("Successfully created database engine")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    return engine

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def get_db() -> Generator[Session, None, None]:
    """
    Создание новой сессии базы данных для каждого запроса
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully initialized database")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise 