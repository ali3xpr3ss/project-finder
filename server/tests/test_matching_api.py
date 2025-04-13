from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate
from schemas.user import UserCreate
from main import app

client = TestClient(app)

def test_get_matching_profiles_api(db: Session, test_user: User):
    """Тест API получения подходящих участников для проекта"""
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
    
    # Тестируем API
    response = client.get(f"/api/matching/projects/{project.id}/matching-profiles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("profile" in item and "score" in item for item in data)

def test_get_matching_projects_api(db: Session, test_user: User):
    """Тест API получения подходящих проектов для участника"""
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
    
    # Тестируем API
    response = client.get(f"/api/matching/users/{user.id}/matching-projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("project" in item and "score" in item for item in data)

def test_get_compatibility_api(db: Session, test_user: User):
    """Тест API получения оценки совместимости"""
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
    
    # Тестируем API
    response = client.get(f"/api/matching/compatibility/{project.id}/{user.id}")
    assert response.status_code == 200
    compatibility = response.json()
    assert 0 <= compatibility <= 1

def test_get_recommendations_api(db: Session, test_user: User):
    """Тест API получения рекомендаций"""
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
    
    # Тестируем API
    response = client.get(f"/api/matching/users/{users[0].id}/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "matching_projects" in data
    assert "similar_profiles" in data
    assert len(data["matching_projects"]) > 0
    assert len(data["similar_profiles"]) > 0
    assert all(profile["profile"]["id"] != users[0].id for profile in data["similar_profiles"]) 