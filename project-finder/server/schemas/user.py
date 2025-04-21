from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    description: Optional[str] = None
    skills: List[str] = []
    experience: Optional[str] = None
    telegram_username: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    telegram_username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 