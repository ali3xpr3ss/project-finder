from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from sqlalchemy import or_, and_
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy.sql import text

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: ProjectCreate, user_id: int) -> Project:
    db_project = Project(
        **project.dict(),
        team_lead_id=user_id
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
    if db_project:
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

def search_projects_db(
    db: Session,
    filters: Dict,
    skip: int = 0,
    limit: int = 20
) -> List[Project]:
    query = db.query(Project)
    
    # Безопасный поиск по тексту
    if filters.get("query"):
        search_terms = [term.strip() for term in filters["query"].split()]
        search_conditions = []
        for term in search_terms:
            search_conditions.append(
                or_(
                    Project.title.ilike(f"%{term}%"),
                    Project.description.ilike(f"%{term}%")
                )
            )
        query = query.filter(and_(*search_conditions))
    
    # Поиск по навыкам через overlap
    if filters.get("skills"):
        query = query.filter(Project.required_skills.overlap(filters["skills"]))
    
    # Точное соответствие статуса
    if filters.get("status"):
        query = query.filter(Project.status == filters["status"])
    
    # Добавляем сортировку по релевантности и дате
    query = query.order_by(Project.created_at.desc())
    
    return query.offset(skip).limit(limit).all() 