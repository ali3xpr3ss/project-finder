from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: ProjectCreate, user_id: int) -> Project:
    db_project = Project(
        title=project.title,
        description=project.description,
        required_roles=project.required_roles,
        technologies=project.technologies,
        team_lead_id=user_id,
        status=project.status
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Project:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> None:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(db_project)
    db.commit()

def like_project(db: Session, project_id: int, user_id: int) -> Project:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user in db_project.liked_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already liked"
        )
    
    db_project.liked_by.append(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project

def unlike_project(db: Session, project_id: int, user_id: int) -> Project:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user not in db_project.liked_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not liked"
        )
    
    db_project.liked_by.remove(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project 