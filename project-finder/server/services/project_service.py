from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate
from services.semantic_search import semantic_search
from datetime import datetime

class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_project(self, project_id: int) -> Optional[Project]:
        """Получение проекта по ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_project_by_name(self, name: str, user_id: int) -> Optional[Project]:
        """Получение проекта по названию для конкретного пользователя"""
        return self.db.query(Project).filter(
            Project.name == name,
            Project.user_id == user_id
        ).first()

    def get_user_projects(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """Получение всех проектов пользователя"""
        return self.db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()

    def create_project(self, project: ProjectCreate, user_id: int) -> Project:
        """Создание нового проекта"""
        # Проверяем уникальность названия проекта для текущего пользователя
        existing_project = self.db.query(Project).filter(
            Project.name == project.name,
            Project.user_id == user_id
        ).first()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this name already exists"
            )
        
        db_project = Project(
            title=project.title,
            description=project.description,
            required_skills=project.required_skills,
            required_experience=project.required_experience,
            technologies=project.technologies,
            status=project.status,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def update_project(self, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """Обновление проекта"""
        db_project = self.get_project(project_id)
        if not db_project:
            return None
        
        # Проверяем уникальность названия при обновлении
        if project_update.name and project_update.name != db_project.name:
            existing_project = self.db.query(Project).filter(
                Project.name == project_update.name,
                Project.user_id == db_project.user_id,
                Project.id != project_id
            ).first()
            
            if existing_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project with this name already exists"
                )
        
        # Обновляем только переданные поля
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db_project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int) -> bool:
        """Удаление проекта"""
        db_project = self.get_project(project_id)
        if not db_project:
            return False
        
        self.db.delete(db_project)
        self.db.commit()
        return True

    def get_all_projects(self, current_user: User) -> List[Project]:
        """Получение всех проектов (только для администраторов)"""
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view all projects"
            )
        return self.db.query(Project).all()

    def like_project(self, project_id: int, user_id: int) -> bool:
        """Лайк проекта"""
        db_project = self.get_project(project_id)
        if not db_project:
            return False
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if user not in db_project.likes:
            db_project.likes.append(user)
            self.db.commit()
        return True

    def unlike_project(self, project_id: int, user_id: int) -> bool:
        """Удаление лайка проекта"""
        db_project = self.get_project(project_id)
        if not db_project:
            return False
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if user in db_project.likes:
            db_project.likes.remove(user)
            self.db.commit()
        return True

    def search_projects(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        technologies: Optional[List[str]] = None,
        required_roles: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Project]:
        """Поиск и фильтрация проектов с использованием семантического поиска"""
        # Получаем все проекты
        projects = self.db.query(Project).all()
        
        # Применяем фильтры
        if status:
            projects = [p for p in projects if p.status == status]
        if technologies:
            projects = [p for p in projects if all(t in (p.technologies or []) for t in technologies)]
        if required_roles:
            projects = [p for p in projects if all(r in (p.required_roles or []) for r in required_roles)]
        if is_active is not None:
            projects = [p for p in projects if p.is_active == is_active]
        
        # Если есть поисковый запрос, используем семантический поиск
        if query:
            # Индексируем отфильтрованные проекты
            semantic_search.index_projects(projects)
            # Получаем результаты с оценками релевантности
            search_results = semantic_search.search(query, top_k=len(projects))
            # Извлекаем только проекты из результатов
            projects = [project for project, _ in search_results]
        
        # Применяем пагинацию
        return projects[skip:skip + limit]

    def get_projects_by_technology(self, technology: str) -> List[Project]:
        """Получение проектов по технологии"""
        return self.db.query(Project).filter(Project.technologies.contains([technology])).all()

    def get_projects_by_role(self, role: str) -> List[Project]:
        """Получение проектов по требуемой роли"""
        return self.db.query(Project).filter(Project.required_roles.contains([role])).all()

    def get_projects_by_status(self, status: str) -> List[Project]:
        """Получение проектов по статусу"""
        return self.db.query(Project).filter(Project.status == status).all()

    def get_active_projects(self) -> List[Project]:
        """Получение активных проектов"""
        return self.db.query(Project).filter(Project.is_active == True).all()

    def get_project_statistics(self) -> dict:
        """Получение статистики по проектам"""
        total_projects = self.db.query(Project).count()
        active_projects = self.db.query(Project).filter(Project.is_active == True).count()
        completed_projects = self.db.query(Project).filter(Project.status == "completed").count()
        on_hold_projects = self.db.query(Project).filter(Project.status == "on_hold").count()
        
        # Получаем топ технологий
        all_technologies = []
        for project in self.db.query(Project).all():
            all_technologies.extend(project.technologies or [])
        technology_counts = {}
        for tech in all_technologies:
            technology_counts[tech] = technology_counts.get(tech, 0) + 1
        top_technologies = sorted(technology_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Получаем топ требуемых ролей
        all_roles = []
        for project in self.db.query(Project).all():
            all_roles.extend(project.required_roles or [])
        role_counts = {}
        for role in all_roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        top_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "on_hold_projects": on_hold_projects,
            "top_technologies": dict(top_technologies),
            "top_roles": dict(top_roles)
        }

    def get_project_stats(self) -> Dict[str, Any]:
        """Получает статистику по проектам"""
        total_projects = self.db.query(func.count(Project.id)).scalar()
        active_projects = self.db.query(func.count(Project.id)).filter(Project.is_active == True).scalar()
        
        # Подсчет технологий
        all_technologies: List[str] = []
        projects = self.db.query(Project).all()
        for project in projects:
            all_technologies.extend(project.technologies)
        
        technology_counts: Dict[str, int] = {}
        for tech in all_technologies:
            technology_counts[tech] = technology_counts.get(tech, 0) + 1
        
        # Подсчет ролей
        all_roles: List[str] = []
        for project in projects:
            all_roles.extend(project.required_roles)
        
        role_counts: Dict[str, int] = {}
        for role in all_roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "technology_stats": technology_counts,
            "role_stats": role_counts
        } 