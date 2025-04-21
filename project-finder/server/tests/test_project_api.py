import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import User
from schemas.project import ProjectCreate
from main import app

client = TestClient(app)

def test_create_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест создания проекта через API"""
    project_data = {
        "name": "Test Project",
        "description": "Test Description",
        "required_roles": ["developer", "designer"],
        "technologies": ["Python", "FastAPI", "React"]
    }
    
    response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["description"] == project_data["description"]
    assert data["required_roles"] == project_data["required_roles"]
    assert data["technologies"] == project_data["technologies"]
    assert data["user_id"] == test_user.id
    assert data["is_active"] is True
    assert data["status"] == "active"

def test_create_project_unauthorized():
    """Тест создания проекта без авторизации"""
    project_data = {"name": "Test Project"}
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 401

def test_get_user_projects_api(db: Session, test_user: User, test_user_token: str):
    """Тест получения проектов пользователя через API"""
    # Создаем несколько проектов
    project_data = {"name": "Test Project"}
    for _ in range(3):
        client.post(
            "/api/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    
    response = client.get(
        "/api/projects/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(p["user_id"] == test_user.id for p in data)

def test_get_all_projects_api(db: Session, test_user: User, test_admin: User, test_admin_token: str):
    """Тест получения всех проектов через API"""
    # Создаем проект от обычного пользователя
    project_data = {"name": "Test Project"}
    client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Проверяем доступ для администратора
    response = client.get(
        "/api/projects/all",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест получения проекта по ID через API"""
    # Создаем проект
    project_data = {"name": "Test Project"}
    create_response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Получаем проект
    response = client.get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == project_data["name"]

def test_update_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест обновления проекта через API"""
    # Создаем проект
    project_data = {"name": "Test Project"}
    create_response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Обновляем проект
    update_data = {
        "name": "Updated Project",
        "description": "Updated Description",
        "status": "on_hold"
    }
    
    response = client.put(
        f"/api/projects/{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]

def test_delete_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест удаления проекта через API"""
    # Создаем проект
    project_data = {"name": "Test Project"}
    create_response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Удаляем проект
    response = client.delete(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    
    # Проверяем, что проект удален
    get_response = client.get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert get_response.status_code == 404

def test_like_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест лайка проекта через API"""
    # Создаем проект
    project_data = {"name": "Test Project"}
    create_response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Лайкаем проект
    response = client.post(
        f"/api/projects/{project_id}/like",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["likes_count"] == 1

def test_unlike_project_api(db: Session, test_user: User, test_user_token: str):
    """Тест удаления лайка проекта через API"""
    # Создаем проект
    project_data = {"name": "Test Project"}
    create_response = client.post(
        "/api/projects/",
        json=project_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Лайкаем проект
    client.post(
        f"/api/projects/{project_id}/like",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Удаляем лайк
    response = client.delete(
        f"/api/projects/{project_id}/like",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["likes_count"] == 0 