from typing import List, Optional
from pydantic import BaseModel, Field, constr
from datetime import datetime

class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    title: constr(min_length=1, max_length=100)
    description: constr(min_length=10, max_length=2000)
    required_skills: List[str] = Field(default_factory=list, min_items=1)
    status: str = Field(pattern="^(active|completed|pending)$")

class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    team_size: int = Field(gt=0, lt=100)
    deadline: Optional[datetime] = None

class ProjectUpdate(ProjectBase):
    """Схема для обновления проекта"""
    title: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[constr(min_length=10, max_length=2000)] = None
    required_skills: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|pending)$")
    team_size: Optional[int] = Field(None, gt=0, lt=100)
    deadline: Optional[datetime] = None

class ProjectSearch(BaseModel):
    query: constr(min_length=1, max_length=100)
    skills: Optional[List[str]] = Field(None, min_items=1)
    status: Optional[str] = Field(None, pattern="^(active|completed|pending)$")

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