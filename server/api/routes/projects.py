from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.services.user_service import get_current_user
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate, Project, ProjectSearch
from api.services.project_service import (
    create_project,
    get_project,
    get_projects,
    update_project,
    delete_project,
    search_projects_db
)
from fastapi_limiter.depends import RateLimiter
from core.database import transaction

router = APIRouter()

@router.get("/search/", response_model=List[Project])
def search_projects(
    query: str = Query(..., min_length=1, max_length=100),
    skills: Optional[List[str]] = Query(None, min_items=1, max_items=20),
    status: Optional[str] = Query(None, regex="^(active|completed|pending)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Поиск проектов по:
    - текстовому запросу (в названии и описании)
    - требуемым навыкам
    - статусу проекта
    """
    filters = ProjectSearch(
        query=query,
        skills=skills,
        status=status
    )
    return search_projects_db(db=db, filters=filters.dict(), skip=skip, limit=limit)

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_projects(db=db, skip=skip, limit=limit)

@router.post("/", response_model=Project)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    with transaction(db):
        return create_project(db=db, project=project, user_id=current_user.id)

@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=Project)
def update_project_details(
    project_update: ProjectUpdate,
    project_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    with transaction(db):
        project = get_project(db=db, project_id=project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.team_lead_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return update_project(db=db, project_id=project_id, project_update=project_update)

@router.delete("/{project_id}")
def delete_project_by_id(
    project_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    with transaction(db):
        project = get_project(db=db, project_id=project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.team_lead_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        delete_project(db=db, project_id=project_id)
        return {"message": "Project deleted successfully"} 