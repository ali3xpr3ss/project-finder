from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    title: str
    description: Optional[str] = None
    required_roles: List[str] = []
    technologies: List[str] = []
    status: str = "active"

class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    pass

class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    title: Optional[str] = None
    description: Optional[str] = None
    required_roles: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    status: Optional[str] = None

class Project(ProjectBase):
    """Схема проекта"""
    id: int
    team_lead_id: int
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_liked: bool = False

    class Config:
        from_attributes = True 