import pytest
from fastapi.testclient import TestClient
from main import app
from api.services.user_service import create_user
from schemas.user import UserCreate
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from core.config import settings

def test_register_user(client: TestClient, db_session: Session):
    # Тестовые данные
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "role": "user"
    }
    
    # Отправляем запрос на регистрацию
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["role"] == user_data["role"]
    assert "password" not in data  # Пароль не должен возвращаться
    
    # Проверяем валидацию email
    invalid_email_data = user_data.copy()
    invalid_email_data["email"] = "invalid-email"
    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response.status_code == 422  # Validation Error
    assert "Invalid email format" in response.json()["detail"]
    
    # Проверяем валидацию роли
    invalid_role_data = user_data.copy()
    invalid_role_data["role"] = "invalid_role"
    response = client.post("/api/v1/auth/register", json=invalid_role_data)
    assert response.status_code == 422  # Validation Error
    assert "Invalid role" in response.json()["detail"]
    
    # Проверяем дублирование email
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    
    # Проверяем валидацию пароля
    invalid_password_data = user_data.copy()
    invalid_password_data["email"] = "test2@example.com"
    invalid_password_data["password"] = "weak"  # Слишком слабый пароль
    response = client.post("/api/v1/auth/register", json=invalid_password_data)
    assert response.status_code == 400
    assert "Password must be at least 8 characters long" in response.json()["detail"]
    
    # Проверяем пустые поля
    empty_data = {
        "email": "",
        "password": "",
        "name": "",
        "role": ""
    }
    response = client.post("/api/v1/auth/register", json=empty_data)
    assert response.status_code == 422
    assert "field required" in response.json()["detail"][0]["msg"]

def test_login_user(client: TestClient, db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    create_user(db_session, user_data)
    
    # Отправляем запрос на вход
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Проверяем токен
    token = data["access_token"]
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == user_data.email
    assert payload["type"] == "access"
    
    # Проверяем срок действия токена
    assert datetime.fromtimestamp(payload["exp"]) > datetime.utcnow()
    
    # Проверяем максимальную длину пароля
    long_password_data = login_data.copy()
    long_password_data["password"] = "A" * 129  # Максимальная длина + 1
    response = client.post("/api/v1/auth/login", data=long_password_data)
    assert response.status_code == 422
    assert "Password must not exceed 128 characters" in response.json()["detail"]
    
    # Проверяем блокировку аккаунта
    for _ in range(5):
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 403
    assert "Account is locked" in response.json()["detail"]
    
    # Проверяем пустые поля
    empty_data = {
        "username": "",
        "password": ""
    }
    response = client.post("/api/v1/auth/login", data=empty_data)
    assert response.status_code == 422
    assert "field required" in response.json()["detail"][0]["msg"]
    
    # Проверяем неверный формат данных
    invalid_data = {
        "username": "test@example.com",
        "password": 123  # Пароль должен быть строкой
    }
    response = client.post("/api/v1/auth/login", data=invalid_data)
    assert response.status_code == 422
    assert "type_error" in response.json()["detail"][0]["msg"]

def test_get_current_user_info(client: TestClient, db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    create_user(db_session, user_data)
    
    # Создаем токен
    token_data = {
        "sub": user_data.email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access"
    }
    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    # Отправляем запрос на получение информации о пользователе
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data.email
    assert data["name"] == user_data.name
    assert data["role"] == user_data.role
    
    # Проверяем неактивного пользователя
    user = get_user_by_email(db_session, user_data.email)
    user.is_active = False
    db_session.commit()
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "User account is inactive" in response.json()["detail"]
    
    # Проверяем истекший токен
    expired_token_data = {
        "sub": user_data.email,
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "type": "access"
    }
    expired_token = jwt.encode(expired_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]
    
    # Проверяем неверный формат токена
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]
    
    # Проверяем отсутствие токена
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
    
    # Проверяем некорректные заголовки авторизации
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code == 401
    assert "Invalid authorization header" in response.json()["detail"]
    
    # Проверяем пустой токен
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401
    assert "Token is required" in response.json()["detail"]
    
    # Проверяем токен с неверным типом
    refresh_token_data = {
        "sub": user_data.email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 400
    assert "Invalid token type" in response.json()["detail"]

def test_refresh_token(client: TestClient, db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    create_user(db_session, user_data)
    
    # Получаем токены
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    refresh_token = response.json()["refresh_token"]
    
    # Обновляем токен
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    
    # Проверяем новый токен
    payload = jwt.decode(new_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == user_data.email
    assert payload["type"] == "access"
    assert datetime.fromtimestamp(payload["exp"]) > datetime.utcnow()
    
    # Проверяем неактивного пользователя
    user = get_user_by_email(db_session, user_data.email)
    user.is_active = False
    db_session.commit()
    
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 403
    assert "User account is inactive" in response.json()["detail"]
    
    # Проверяем истекший токен
    expired_token_data = {
        "sub": user_data.email,
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "type": "refresh"
    }
    expired_token = jwt.encode(expired_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_token})
    assert response.status_code == 401
    assert "Refresh token has expired" in response.json()["detail"]
    
    # Проверяем неверный тип токена
    access_token_data = {
        "sub": user_data.email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access"
    }
    access_token = jwt.encode(access_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 400
    assert "Invalid token type" in response.json()["detail"]
    
    # Проверяем неверный формат токена
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]
    
    # Проверяем отсутствие токена
    response = client.post("/api/v1/auth/refresh", json={})
    assert response.status_code == 422
    assert "field required" in response.json()["detail"][0]["msg"]

def test_health_check(client: TestClient):
    # Отправляем запрос на проверку здоровья
    response = client.get("/api/v1/health")
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"  # Проверяем конкретное значение
    assert data["database"] == "connected"  # Проверяем конкретное значение
    assert data["jwt"] == "configured"  # Проверяем конкретное значение
    assert "version" in data
    assert isinstance(data["version"], str)
    assert len(data["version"].split(".")) == 3  # Проверяем формат версии
    
    # Проверяем, что все обязательные поля присутствуют
    required_fields = {"status", "database", "jwt", "version"}
    assert all(field in data for field in required_fields)
    
    # Проверяем, что нет лишних полей
    assert len(data) == len(required_fields)
    
    # Проверяем формат версии
    version_parts = data["version"].split(".")
    assert len(version_parts) == 3
    assert all(part.isdigit() for part in version_parts)
    assert all(int(part) >= 0 for part in version_parts)
    
    # Проверяем, что версия не пустая
    assert all(len(part) > 0 for part in version_parts)
    
    # Проверяем, что версия не слишком длинная
    assert all(len(part) <= 10 for part in version_parts) 