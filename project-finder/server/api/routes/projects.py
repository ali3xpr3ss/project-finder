from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.deps import get_db
from api.services.user_service import get_current_user
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate, Project
from api.services.project_service import (
    create_project,
    get_project,
    get_projects,
    update_project,
    delete_project
)

router = APIRouter()

@router.post("/", response_model=Project)
def create_new_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_project(db=db, project=project, user_id=current_user.id)

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_projects(db=db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int,
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
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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