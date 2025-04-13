from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    roles = Column(JSON)  # Список ролей пользователя
    skills = Column(JSON)  # Список навыков пользователя
    
    # Отношения
    projects = relationship("Project", back_populates="team_lead", cascade="all, delete-orphan")
    member_of = relationship("Project", secondary="project_members")
    liked_projects = relationship("Project", secondary="project_likes", back_populates="liked_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")