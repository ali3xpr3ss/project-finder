from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.project import ProjectCreate, ProjectUpdate, Project
from schemas.user import User
from services.project_service import ProjectService
from api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=Project)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    return await project_service.create_project(project_in, current_user.id)

@router.get("/", response_model=List[Project])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.get_user_projects(current_user.id)

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return await project_service.update_project(project_id, project_in)

@router.delete("/{project_id}", response_model=Project)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return await project_service.delete_project(project_id)

@router.post("/{project_id}/like", response_model=Project)
async def like_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    return await project_service.like_project(project_id, current_user.id)

@router.post("/{project_id}/unlike", response_model=Project)
async def unlike_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_service = ProjectService(db)
    return await project_service.unlike_project(project_id, current_user.id)

@router.get("/search/", response_model=List[Project])
async def search_projects(
    query: str,
    technologies: Optional[List[str]] = None,
    roles: Optional[List[str]] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.search_projects(
        query=query,
        technologies=technologies,
        roles=roles,
        min_experience=min_experience,
        max_experience=max_experience,
        status=status
    )

@router.get("/technology/{technology}", response_model=List[Project])
async def get_projects_by_technology(
    technology: str,
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.get_projects_by_technology(technology)

@router.get("/role/{role}", response_model=List[Project])
async def get_projects_by_role(
    role: str,
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.get_projects_by_role(role)

@router.get("/status/{status}", response_model=List[Project])
async def get_projects_by_status(
    status: str,
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.get_projects_by_status(status)

@router.get("/active/", response_model=List[Project])
async def get_active_projects(
    db: Session = Depends(get_db)
) -> List[Project]:
    project_service = ProjectService(db)
    return await project_service.get_active_projects()

@router.get("/statistics/", response_model=dict)
async def get_project_statistics(
    db: Session = Depends(get_db)
) -> dict:
    project_service = ProjectService(db)
    return await project_service.get_project_statistics() 