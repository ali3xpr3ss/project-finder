from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2)
    role: str = Field(min_length=2)
    skills: Optional[List[str]] = []
    experience: Optional[int] = None
    languages: Optional[List[str]] = []
    description: Optional[str] = None
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        return {k: v for k, v in d.items() if v is not None}

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        return {k: v for k, v in d.items() if v is not None}

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "strongpassword",
                "role": "Developer",
                "skills": ["Python", "FastAPI"],
                "experience": 5,
                "languages": ["English", "Russian"],
                "description": "Experienced developer"
            }
        }

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2)
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, min_length=2)
    skills: Optional[List[str]] = None
    experience: Optional[int] = None
    languages: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        return {k: v for k, v in d.items() if v is not None}

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "password": "newstrongpassword",
                "role": "Senior Developer",
                "skills": ["Python", "FastAPI", "Docker"],
                "experience": 6,
                "languages": ["English", "Russian", "Spanish"],
                "description": "Senior developer with extensive experience",
                "is_active": True
            }
        }

class UserInDB(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDB):
    projects: List[Dict[str, Any]] = []

    class Config:
        orm_mode = True

from schemas.project import Project
UserInDB.update_forward_refs()
User.update_forward_refs() 