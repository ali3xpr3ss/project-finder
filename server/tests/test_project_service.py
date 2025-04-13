import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate
from services import project_service

def test_create_project(db: Session, test_user: User):
    """Тест создания проекта"""
    project_data = ProjectCreate(
        name="Test Project",
        description="Test Description",
        required_roles=["developer", "designer"],
        technologies=["Python", "FastAPI", "React"]
    )
    
    project = project_service.create_project(db, project_data, test_user)
    
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert project.required_roles == ["developer", "designer"]
    assert project.technologies == ["Python", "FastAPI", "React"]
    assert project.user_id == test_user.id
    assert project.is_active is True
    assert project.status == "active"

def test_create_project_duplicate_name(db: Session, test_user: User):
    """Тест создания проекта с дублирующимся названием"""
    project_data = ProjectCreate(name="Test Project")
    project_service.create_project(db, project_data, test_user)
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(db, project_data, test_user)
    
    assert exc_info.value.status_code == 400
    assert "Project with this name already exists" in str(exc_info.value.detail)

def test_get_user_projects(db: Session, test_user: User):
    """Тест получения проектов пользователя"""
    # Создаем несколько проектов
    projects = [
        ProjectCreate(name=f"Project {i}") for i in range(3)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    user_projects = project_service.get_user_projects(db, test_user.id)
    assert len(user_projects) == 3
    assert all(p.user_id == test_user.id for p in user_projects)

def test_get_all_projects(db: Session, test_user: User, test_admin: User):
    """Тест получения всех проектов"""
    # Создаем проекты от разных пользователей
    project_data = ProjectCreate(name="Test Project")
    project_service.create_project(db, project_data, test_user)
    
    # Проверяем доступ для обычного пользователя
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_all_projects(db, test_user)
    assert exc_info.value.status_code == 403
    
    # Проверяем доступ для администратора
    projects = project_service.get_all_projects(db, test_admin)
    assert len(projects) == 1

def test_update_project(db: Session, test_user: User):
    """Тест обновления проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    update_data = ProjectUpdate(
        name="Updated Project",
        description="Updated Description",
        status="on_hold"
    )
    
    updated_project = project_service.update_project(db, project.id, update_data, test_user)
    
    assert updated_project.name == "Updated Project"
    assert updated_project.description == "Updated Description"
    assert updated_project.status == "on_hold"

def test_update_project_unauthorized(db: Session, test_user: User, test_admin: User):
    """Тест обновления проекта без прав"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    update_data = ProjectUpdate(name="Updated Project")
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(db, project.id, update_data, test_admin)
    assert exc_info.value.status_code == 403

def test_delete_project(db: Session, test_user: User):
    """Тест удаления проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    deleted_project = project_service.delete_project(db, project.id, test_user)
    assert deleted_project.id == project.id
    
    # Проверяем, что проект действительно удален
    assert project_service.get_project(db, project.id) is None

def test_delete_project_unauthorized(db: Session, test_user: User, test_admin: User):
    """Тест удаления проекта без прав"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.delete_project(db, project.id, test_admin)
    assert exc_info.value.status_code == 403

def test_like_project(db: Session, test_user: User):
    """Тест лайка проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    liked_project = project_service.like_project(db, project.id, test_user)
    assert test_user in liked_project.liked_by

def test_like_project_twice(db: Session, test_user: User):
    """Тест повторного лайка проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    project_service.like_project(db, project.id, test_user)
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.like_project(db, project.id, test_user)
    assert exc_info.value.status_code == 400
    assert "Project already liked" in str(exc_info.value.detail)

def test_unlike_project(db: Session, test_user: User):
    """Тест удаления лайка проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    project_service.like_project(db, project.id, test_user)
    unliked_project = project_service.unlike_project(db, project.id, test_user)
    assert test_user not in unliked_project.liked_by

def test_unlike_project_not_liked(db: Session, test_user: User):
    """Тест удаления несуществующего лайка проекта"""
    project_data = ProjectCreate(name="Test Project")
    project = project_service.create_project(db, project_data, test_user)
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.unlike_project(db, project.id, test_user)
    assert exc_info.value.status_code == 400
    assert "Project not liked" in str(exc_info.value.detail)

def test_project_status_validation(db: Session, test_user: User):
    """Тест валидации статуса проекта"""
    with pytest.raises(ValueError):
        ProjectCreate(
            name="Test Project",
            status="invalid_status"
        )
    
    # Проверяем корректные статусы
    valid_statuses = ["active", "completed", "on_hold"]
    for status in valid_statuses:
        project_data = ProjectCreate(name="Test Project", status=status)
        project = project_service.create_project(db, project_data, test_user)
        assert project.status == status

def test_search_projects(db: Session, test_user: User):
    """Тест поиска проектов"""
    # Создаем тестовые проекты
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"],
            required_roles=["developer", "designer"],
            status="active" if i % 2 == 0 else "completed"
        ) for i in range(5)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    # Тест поиска по названию
    results = project_service.search_projects(db, query="Project 1")
    assert len(results) == 1
    assert results[0].name == "Project 1"
    
    # Тест поиска по описанию
    results = project_service.search_projects(db, query="Description 2")
    assert len(results) == 1
    assert results[0].description == "Description 2"
    
    # Тест фильтрации по статусу
    results = project_service.search_projects(db, status="active")
    assert len(results) == 3
    
    # Тест фильтрации по технологиям
    results = project_service.search_projects(db, technologies=["Python"])
    assert len(results) == 5
    
    # Тест фильтрации по ролям
    results = project_service.search_projects(db, required_roles=["developer"])
    assert len(results) == 5
    
    # Тест пагинации
    results = project_service.search_projects(db, skip=0, limit=2)
    assert len(results) == 2
    results = project_service.search_projects(db, skip=2, limit=2)
    assert len(results) == 2

def test_get_projects_by_technology(db: Session, test_user: User):
    """Тест получения проектов по технологии"""
    # Создаем проекты с разными технологиями
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            technologies=["Python"] if i % 2 == 0 else ["JavaScript"]
        ) for i in range(4)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    python_projects = project_service.get_projects_by_technology(db, "Python")
    assert len(python_projects) == 2
    assert all("Python" in p.technologies for p in python_projects)

def test_get_projects_by_role(db: Session, test_user: User):
    """Тест получения проектов по роли"""
    # Создаем проекты с разными ролями
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            required_roles=["developer"] if i % 2 == 0 else ["designer"]
        ) for i in range(4)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    developer_projects = project_service.get_projects_by_role(db, "developer")
    assert len(developer_projects) == 2
    assert all("developer" in p.required_roles for p in developer_projects)

def test_get_projects_by_status(db: Session, test_user: User):
    """Тест получения проектов по статусу"""
    # Создаем проекты с разными статусами
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            status="active" if i % 2 == 0 else "completed"
        ) for i in range(4)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    active_projects = project_service.get_projects_by_status(db, "active")
    assert len(active_projects) == 2
    assert all(p.status == "active" for p in active_projects)

def test_get_active_projects(db: Session, test_user: User):
    """Тест получения активных проектов"""
    # Создаем проекты с разной активностью
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            is_active=i % 2 == 0
        ) for i in range(4)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    active_projects = project_service.get_active_projects(db)
    assert len(active_projects) == 2
    assert all(p.is_active for p in active_projects)

def test_get_project_statistics(db: Session, test_user: User):
    """Тест получения статистики проектов"""
    # Создаем проекты с разными характеристиками
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            status="active" if i % 2 == 0 else "completed",
            technologies=["Python", "FastAPI"],
            required_roles=["developer", "designer"],
            is_active=True
        ) for i in range(4)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    stats = project_service.get_project_statistics(db)
    
    assert stats["total_projects"] == 4
    assert stats["active_projects"] == 4
    assert stats["completed_projects"] == 2
    assert stats["on_hold_projects"] == 0
    
    assert stats["top_technologies"]["Python"] == 4
    assert stats["top_technologies"]["FastAPI"] == 4
    
    assert stats["top_roles"]["developer"] == 4
    assert stats["top_roles"]["designer"] == 4

def test_semantic_search(db: Session, test_user: User):
    """Тест семантического поиска проектов"""
    # Создаем проекты с разными описаниями
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"],
            required_roles=["developer", "designer"]
        ) for i in range(5)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    # Тест поиска по семантически близким запросам
    results = project_service.search_projects(db, query="Python web application")
    assert len(results) > 0
    assert any("Python" in p.technologies for p in results)
    
    # Тест поиска по синонимам
    results = project_service.search_projects(db, query="web development")
    assert len(results) > 0
    assert any("FastAPI" in p.technologies for p in results)
    
    # Тест поиска по частичному совпадению
    results = project_service.search_projects(db, query="dev")
    assert len(results) > 0
    assert any("developer" in p.required_roles for p in results)

def test_semantic_search_with_filters(db: Session, test_user: User):
    """Тест комбинирования семантического поиска с фильтрами"""
    # Создаем проекты с разными характеристиками
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"] if i % 2 == 0 else ["JavaScript", "React"],
            required_roles=["developer", "designer"],
            status="active" if i % 2 == 0 else "completed"
        ) for i in range(6)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    # Тест поиска с фильтрацией по статусу
    results = project_service.search_projects(
        db,
        query="web development",
        status="active"
    )
    assert len(results) > 0
    assert all(p.status == "active" for p in results)
    
    # Тест поиска с фильтрацией по технологиям
    results = project_service.search_projects(
        db,
        query="frontend development",
        technologies=["React"]
    )
    assert len(results) > 0
    assert all("React" in p.technologies for p in results)
    
    # Тест поиска с фильтрацией по ролям
    results = project_service.search_projects(
        db,
        query="backend development",
        required_roles=["developer"]
    )
    assert len(results) > 0
    assert all("developer" in p.required_roles for p in results)

def test_semantic_search_empty_query(db: Session, test_user: User):
    """Тест поиска с пустым запросом"""
    # Создаем тестовые проекты
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"],
            required_roles=["developer", "designer"]
        ) for i in range(3)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    # Проверяем, что пустой запрос возвращает все проекты
    results = project_service.search_projects(db, query="")
    assert len(results) == 3

def test_semantic_search_no_matches(db: Session, test_user: User):
    """Тест поиска без совпадений"""
    # Создаем тестовые проекты
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"],
            required_roles=["developer", "designer"]
        ) for i in range(3)
    ]
    for project_data in projects:
        project_service.create_project(db, project_data, test_user)
    
    # Проверяем, что поиск по несуществующему запросу возвращает пустой список
    results = project_service.search_projects(db, query="nonexistent technology or skill")
    assert len(results) == 0 