from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Project(Base):
    """Модель проекта"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    required_roles = Column(JSON)  # Список требуемых ролей
    technologies = Column(JSON)  # Список технологий
    team_lead_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active, completed, on_hold
    
    # Отношения
    team_lead = relationship("User", back_populates="projects")
    members = relationship("User", secondary="project_members")
    liked_by = relationship("User", secondary="project_likes", back_populates="liked_projects") 