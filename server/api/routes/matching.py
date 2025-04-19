from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from models.project import Project
from models.user import User
from schemas.project import Project as ProjectSchema
from schemas.user import User as UserSchema
from api.services.matching_service import matching_service
from api.deps import get_db
from api.services.user_service import get_current_user

router = APIRouter(
    prefix="/matching",
    tags=["matching"],
    responses={404: {"description": "Not found"}},
)

@router.get("/projects/{project_id}/matching-profiles", response_model=List[Dict])
async def get_matching_profiles(
    project_id: int = Path(...),
    top_k: Optional[int] = Query(10, description="Количество возвращаемых результатов"),
    min_score: Optional[float] = Query(None, description="Минимальный балл совместимости"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    results = matching_service.find_matching_profiles(project, top_k, min_score)
    return [{"profile": profile, "score": score} for profile, score in results]

@router.get("/users/{user_id}/matching-projects", response_model=List[Dict])
async def get_matching_projects(
    user_id: int = Path(...),
    top_k: Optional[int] = Query(10, description="Количество возвращаемых результатов"),
    min_score: Optional[float] = Query(None, description="Минимальный балл совместимости"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    results = matching_service.find_matching_projects(user, top_k, min_score)
    return [{"project": project, "score": score} for project, score in results]

@router.get("/compatibility/{project_id}/{user_id}", response_model=float)
async def get_compatibility(
    project_id: int = Path(...),
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return matching_service.calculate_compatibility(project, user)

@router.get("/users/{user_id}/recommendations", response_model=Dict)
async def get_recommendations(
    user_id: int = Path(...),
    top_k: Optional[int] = Query(5, description="Количество возвращаемых результатов"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    recommendations = matching_service.get_recommendations(user, top_k)
    return {
        "matching_projects": [
            {"project": project, "score": score}
            for project, score in recommendations["matching_projects"]
        ],
        "similar_profiles": [
            {"profile": profile, "score": score}
            for profile, score in recommendations["similar_profiles"]
        ]
    }