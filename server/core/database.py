from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Создает новую сессию базы данных для каждого запроса
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db() -> None:
    """
    Инициализирует базу данных, создавая все таблицы
    """
    Base.metadata.create_all(bind=engine)

@contextmanager
def transaction(db):
    """
    Контекстный менеджер для управления транзакциями.
    Автоматически выполняет commit при успешном выполнении
    и rollback при возникновении ошибки.
    """
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise 