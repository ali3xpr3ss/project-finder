from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from core.security import get_password_hash, verify_password

# Таблица для связи many-to-many между пользователями и проектами
user_project = Table(
    'user_project',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    skills = Column(String, nullable=True)  # JSON строка
    experience = Column(Integer, nullable=True)
    languages = Column(String, nullable=True)  # JSON строка
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    projects = relationship("Project", secondary=user_project, back_populates="users")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if "password" in kwargs:
            self.hashed_password = get_password_hash(kwargs["password"])

    def dict(self) -> Dict[str, Any]:
        """
        Преобразование объекта пользователя в словарь
        """
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "skills": self.skills,
            "experience": self.experience,
            "languages": self.languages,
            "description": self.description,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def verify_password(self, password: str) -> bool:
        """
        Проверка пароля пользователя
        """
        return verify_password(password, self.hashed_password)

    def update(self, **kwargs: Any) -> None:
        """
        Обновление данных пользователя
        """
        for key, value in kwargs.items():
            if key == "password":
                self.hashed_password = get_password_hash(value)
            else:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow() 