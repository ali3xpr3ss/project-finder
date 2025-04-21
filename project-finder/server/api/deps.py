from typing import Generator
from sqlalchemy.orm import Session
from core.database import get_db

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

__all__ = ["get_db"] 