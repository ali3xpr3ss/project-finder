from fastapi import APIRouter, Depends, HTTPException, status, Query
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
    project_id: int,
    top_k: Optional[int] = Query(10, description="Количество возвращаемых результатов"),
    min_score: Optional[float] = Query(None, description="Минимальный балл совместимости"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение подходящих участников для проекта.
    
    ## Параметры
    * `project_id` - ID проекта
    * `top_k` - количество возвращаемых результатов (по умолчанию 10)
    * `min_score` - минимальный балл совместимости (опционально)
    
    ## Возвращает
    Список словарей, где каждый словарь содержит:
    * `profile` - информация об участнике
    * `score` - балл совместимости (от 0 до 1)
    
    ## Пример ответа
    ```json
    [
        {
            "profile": {
                "id": 1,
                "name": "John Doe",
                "technologies": ["Python", "FastAPI"],
                "roles": ["backend developer"]
            },
            "score": 0.85
        }
    ]
    ```
    """
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
    user_id: int,
    top_k: Optional[int] = Query(10, description="Количество возвращаемых результатов"),
    min_score: Optional[float] = Query(None, description="Минимальный балл совместимости"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение подходящих проектов для участника.
    
    ## Параметры
    * `user_id` - ID участника
    * `top_k` - количество возвращаемых результатов (по умолчанию 10)
    * `min_score` - минимальный балл совместимости (опционально)
    
    ## Возвращает
    Список словарей, где каждый словарь содержит:
    * `project` - информация о проекте
    * `score` - балл совместимости (от 0 до 1)
    
    ## Пример ответа
    ```json
    [
        {
            "project": {
                "id": 1,
                "name": "Web Application",
                "technologies": ["Python", "FastAPI"],
                "required_roles": ["backend developer"]
            },
            "score": 0.92
        }
    ]
    ```
    """
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
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение оценки совместимости проекта и участника.
    
    ## Параметры
    * `project_id` - ID проекта
    * `user_id` - ID участника
    
    ## Возвращает
    Балл совместимости от 0 до 1, где:
    * 1 - полная совместимость
    * 0 - полная несовместимость
    
    ## Пример ответа
    ```json
    0.85
    ```
    """
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
    user_id: int,
    top_k: Optional[int] = Query(5, description="Количество возвращаемых результатов"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение рекомендаций для участника.
    
    ## Параметры
    * `user_id` - ID участника
    * `top_k` - количество возвращаемых результатов (по умолчанию 5)
    
    ## Возвращает
    Словарь, содержащий:
    * `matching_projects` - список подходящих проектов
    * `similar_profiles` - список похожих участников
    
    ## Пример ответа
    ```json
    {
        "matching_projects": [
            {
                "project": {
                    "id": 1,
                    "name": "Web Application",
                    "technologies": ["Python", "FastAPI"]
                },
                "score": 0.92
            }
        ],
        "similar_profiles": [
            {
                "profile": {
                    "id": 2,
                    "name": "Jane Smith",
                    "technologies": ["Python", "FastAPI"]
                },
                "score": 0.88
            }
        ]
    }
    ```
    """
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