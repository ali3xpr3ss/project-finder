import pytest
from sqlalchemy.orm import Session
from models.project import Project
from models.user import User
from services.matching_service import matching_service
from schemas.project import ProjectCreate
from schemas.user import UserCreate

def test_find_matching_profiles(db: Session, test_user: User):
    """Тест поиска подходящих участников для проекта"""
    # Создаем тестовый проект
    project_data = ProjectCreate(
        name="Python Web Project",
        description="Разработка веб-приложения на Python и FastAPI",
        technologies=["Python", "FastAPI", "PostgreSQL"],
        required_roles=["backend developer", "frontend developer"],
        status="active"
    )
    project = Project(**project_data.dict(), user_id=test_user.id)
    db.add(project)
    db.commit()
    
    # Создаем тестовые анкеты
    profiles = [
        UserCreate(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password="testpassword123",
            bio=f"Bio {i}",
            skills=f"Skills {i}",
            experience=f"Experience {i}",
            education=f"Education {i}",
            technologies=["Python", "FastAPI"] if i % 2 == 0 else ["JavaScript", "React"],
            roles=["backend developer", "frontend developer"],
            languages=["English", "Russian"]
        ) for i in range(5)
    ]
    
    # Создаем пользователей в базе
    users = []
    for profile in profiles:
        user = User(**profile.dict())
        db.add(user)
        users.append(user)
    db.commit()
    
    # Индексируем анкеты
    from services.profile_search import profile_search
    profile_search.index_profiles(users)
    
    # Ищем подходящих участников
    results = matching_service.find_matching_profiles(project)
    
    # Проверяем результаты
    assert len(results) > 0
    assert any("Python" in profile[0]["technologies"] for profile in results)
    assert any("backend developer" in profile[0]["roles"] for profile in results)

def test_find_matching_projects(db: Session, test_user: User):
    """Тест поиска подходящих проектов для участника"""
    # Создаем тестовые проекты
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"] if i % 2 == 0 else ["JavaScript", "React"],
            required_roles=["backend developer", "frontend developer"],
            status="active"
        ) for i in range(5)
    ]
    
    for project_data in projects:
        project = Project(**project_data.dict(), user_id=test_user.id)
        db.add(project)
    db.commit()
    
    # Создаем тестовую анкету
    profile = UserCreate(
        name="Test User",
        email="test@example.com",
        password="testpassword123",
        bio="Python developer with 5 years of experience",
        skills="Python, FastAPI, PostgreSQL",
        experience="5 years of backend development",
        education="Computer Science",
        technologies=["Python", "FastAPI", "PostgreSQL"],
        roles=["backend developer"],
        languages=["English", "Russian"]
    )
    
    user = User(**profile.dict())
    db.add(user)
    db.commit()
    
    # Индексируем проекты
    from services.semantic_search import semantic_search
    semantic_search.index_projects(projects)
    
    # Ищем подходящие проекты
    results = matching_service.find_matching_projects(user)
    
    # Проверяем результаты
    assert len(results) > 0
    assert any("Python" in project[0]["technologies"] for project in results)
    assert any("backend developer" in project[0]["required_roles"] for project in results)

def test_calculate_compatibility(db: Session, test_user: User):
    """Тест расчета совместимости проекта и участника"""
    # Создаем тестовый проект
    project_data = ProjectCreate(
        name="Python Web Project",
        description="Разработка веб-приложения на Python и FastAPI",
        technologies=["Python", "FastAPI", "PostgreSQL"],
        required_roles=["backend developer"],
        status="active"
    )
    project = Project(**project_data.dict(), user_id=test_user.id)
    db.add(project)
    db.commit()
    
    # Создаем тестовую анкету
    profile = UserCreate(
        name="Test User",
        email="test@example.com",
        password="testpassword123",
        bio="Python developer with 5 years of experience",
        skills="Python, FastAPI, PostgreSQL",
        experience="5 years of backend development",
        education="Computer Science",
        technologies=["Python", "FastAPI", "PostgreSQL"],
        roles=["backend developer"],
        languages=["English", "Russian"]
    )
    
    user = User(**profile.dict())
    db.add(user)
    db.commit()
    
    # Рассчитываем совместимость
    compatibility = matching_service.calculate_compatibility(project, user)
    
    # Проверяем результат
    assert 0 <= compatibility <= 1
    assert compatibility >= matching_service.min_compatibility_score

def test_get_recommendations(db: Session, test_user: User):
    """Тест получения рекомендаций для участника"""
    # Создаем тестовые проекты
    projects = [
        ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}",
            technologies=["Python", "FastAPI"] if i % 2 == 0 else ["JavaScript", "React"],
            required_roles=["backend developer", "frontend developer"],
            status="active"
        ) for i in range(5)
    ]
    
    for project_data in projects:
        project = Project(**project_data.dict(), user_id=test_user.id)
        db.add(project)
    db.commit()
    
    # Создаем тестовые анкеты
    profiles = [
        UserCreate(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password="testpassword123",
            bio=f"Bio {i}",
            skills=f"Skills {i}",
            experience=f"Experience {i}",
            education=f"Education {i}",
            technologies=["Python", "FastAPI"] if i % 2 == 0 else ["JavaScript", "React"],
            roles=["backend developer", "frontend developer"],
            languages=["English", "Russian"]
        ) for i in range(5)
    ]
    
    # Создаем пользователей в базе
    users = []
    for profile in profiles:
        user = User(**profile.dict())
        db.add(user)
        users.append(user)
    db.commit()
    
    # Индексируем проекты и анкеты
    from services.semantic_search import semantic_search
    from services.profile_search import profile_search
    semantic_search.index_projects(projects)
    profile_search.index_profiles(users)
    
    # Получаем рекомендации
    recommendations = matching_service.get_recommendations(users[0])
    
    # Проверяем результаты
    assert 'matching_projects' in recommendations
    assert 'similar_profiles' in recommendations
    assert len(recommendations['matching_projects']) > 0
    assert len(recommendations['similar_profiles']) > 0
    assert all(profile[0]['id'] != users[0].id for profile in recommendations['similar_profiles']) 