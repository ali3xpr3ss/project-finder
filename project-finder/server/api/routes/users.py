from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from api.services.user_service import (
    get_user,
    get_current_user
)
from schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user 