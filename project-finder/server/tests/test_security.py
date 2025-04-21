import pytest
from fastapi.testclient import TestClient
from api.services.user_service import create_user
from schemas.user import UserCreate
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from core.config import settings
from fastapi import HTTPException
import time

def test_password_hashing(db_session: Session):
    """Проверка правильности хеширования паролей"""
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",  # Более сложный пароль
        name="Test User",
        role="user"
    )
    user = create_user(db_session, user_data)
    
    # Проверяем, что хеш пароля не совпадает с оригинальным паролем
    assert user.hashed_password != user_data.password
    # Проверяем, что хеш пароля не содержит оригинальный пароль
    assert user_data.password not in user.hashed_password
    # Проверяем, что хеш пароля не содержит чувствительные данные
    assert "password" not in user.hashed_password.lower()
    assert "test" not in user.hashed_password.lower()

def test_jwt_token_security(client: TestClient, db_session: Session):
    """Проверка безопасности JWT токенов"""
    # Создаем пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    create_user(db_session, user_data)
    
    # Получаем токен
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    # Проверяем, что токен не содержит чувствительных данных
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert "password" not in payload
    assert "hashed_password" not in payload
    assert "email" not in payload  # email не должен быть в payload
    
    # Проверяем тип токена
    assert payload["type"] == "access"
    
    # Проверяем, что токен имеет срок действия
    assert "exp" in payload
    assert datetime.fromtimestamp(payload["exp"]) > datetime.utcnow()
    
    # Проверяем, что токен не содержит лишних данных
    allowed_fields = {"sub", "exp", "type"}
    assert all(field in allowed_fields for field in payload.keys())

def test_rate_limiting(client: TestClient):
    # Создаем тестового пользователя
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "role": "user"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    # Отправляем множество запросов с неверным паролем
    failed_attempts = []
    for _ in range(100):  # Максимальное количество попыток
        response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "WrongPassword123!"}
        )
        failed_attempts.append(response.status_code)
        
        if response.status_code == 429:  # Too Many Requests
            break
    
    # Проверяем, что некоторые запросы получили статус 429
    assert 429 in failed_attempts
    
    # Проверяем, что после успешного входа система снова позволяет попытки
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    assert response.status_code == 200
    
    # Проверяем, что после успешного входа можно снова делать запросы
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "WrongPassword123!"}
        )
        assert response.status_code != 429

def test_sql_injection_protection(client: TestClient, db_session: Session):
    """Проверка защиты от SQL-инъекций"""
    # Пытаемся использовать различные SQL-инъекции
    malicious_emails = [
        "test@example.com' OR '1'='1",
        "test@example.com'; DROP TABLE users; --",
        "test@example.com' UNION SELECT * FROM users; --",
        "test@example.com' OR '1'='1' --",
        "test@example.com' OR 'x'='x"
    ]
    
    for malicious_email in malicious_emails:
        user_data = {
            "email": malicious_email,
            "password": "TestPassword123!",
            "name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation Error
        assert "Invalid email format" in response.json()["detail"]

def test_xss_protection(client: TestClient, db_session: Session):
    """Проверка защиты от XSS-атак"""
    # Пытаемся использовать различные XSS-атаки
    xss_names = [
        "<script>alert('xss')</script>",
        "<img src='x' onerror='alert(1)'>",
        "<svg onload='alert(1)'>",
        "javascript:alert(1)",
        "<div onmouseover='alert(1)'>",
        "<input onfocus='alert(1)'>",
        "<body onload='alert(1)'>",
        "<a href='javascript:alert(1)'>",
        "<img src='data:image/svg+xml;base64,PHN2Zy9vbmxvYWQ9YWxlcnQoMSk+'>"
    ]
    
    for xss_name in xss_names:
        user_data = UserCreate(
            email=f"test{xss_name}@example.com",
            password="TestPassword123!",
            name=xss_name,
            role="user"
        )
        user = create_user(db_session, user_data)
        
        # Проверяем, что скрипты и опасные теги не были сохранены как есть
        assert "<script>" not in user.name
        assert "<img" not in user.name
        assert "<svg" not in user.name
        assert "javascript:" not in user.name
        assert "onerror" not in user.name
        assert "onload" not in user.name
        assert "onmouseover" not in user.name
        assert "onfocus" not in user.name
        assert "onload" not in user.name
        
        # Проверяем, что специальные символы были экранированы
        assert "&lt;" in user.name
        assert "&gt;" in user.name
        assert "&quot;" in user.name
        assert "&#x27;" in user.name

def test_csrf_protection(client: TestClient):
    """Проверка защиты от CSRF-атак"""
    # Проверяем, что токен не передается через cookie
    response = client.get("/api/v1/users/me")
    assert "Set-Cookie" not in response.headers
    
    # Проверяем, что запросы без токена отклоняются
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "role": "user"
    })
    assert response.status_code == 401
    
    # Проверяем, что запросы с неверным токеном отклоняются
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    
    # Проверяем, что запросы с токеном в cookie игнорируются
    response = client.get(
        "/api/v1/users/me",
        headers={"Cookie": "token=valid_token"}
    )
    assert response.status_code == 401

def test_password_validation(db_session: Session):
    """Проверка валидации пароля"""
    # Проверяем минимальную длину пароля
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="123",  # Слишком короткий пароль
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must be at least 8 characters long" in str(exc_info.value.detail)
    
    # Проверяем наличие цифр
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="testpassword",  # Пароль без цифр
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must contain at least one number" in str(exc_info.value.detail)
    
    # Проверяем наличие букв
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="12345678",  # Пароль только с цифрами
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must contain at least one letter" in str(exc_info.value.detail)
    
    # Проверяем наличие специальных символов
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123",  # Пароль без специальных символов
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must contain at least one special character" in str(exc_info.value.detail)
    
    # Проверяем наличие заглавных букв
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="testpassword123!",  # Пароль без заглавных букв
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must contain at least one uppercase letter" in str(exc_info.value.detail)
    
    # Проверяем наличие строчных букв
    with pytest.raises(HTTPException) as exc_info:
        user_data = UserCreate(
            email="test@example.com",
            password="TESTPASSWORD123!",  # Пароль без строчных букв
            name="Test User",
            role="user"
        )
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Password must contain at least one lowercase letter" in str(exc_info.value.detail)

def test_token_validation(client: TestClient, db_session: Session):
    """Проверка валидации токена"""
    # Создаем пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        name="Test User",
        role="user"
    )
    create_user(db_session, user_data)
    
    # Получаем токен
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    # Проверяем тип токена
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["type"] == "access"
    
    # Проверяем срок действия токена
    assert datetime.fromtimestamp(payload["exp"]) > datetime.utcnow()
    
    # Проверяем неверный тип токена
    refresh_token = response.json()["refresh_token"]
    with pytest.raises(HTTPException) as exc_info:
        client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert exc_info.value.status_code == 400
    assert "Invalid token type" in str(exc_info.value.detail)

def test_account_lockout(client: TestClient, db_session: Session):
    # Создаем тестового пользователя
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "role": "user"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    # Пытаемся войти с неверным паролем несколько раз
    for _ in range(5):  # Максимальное количество попыток
        response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "WrongPassword123!"}
        )
        assert response.status_code == 401
    
    # Проверяем, что аккаунт заблокирован
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    assert response.status_code == 403
    assert "Account is locked" in response.json()["detail"]
    
    # Проверяем время блокировки
    user = get_user_by_email(db_session, user_data["email"])
    assert user.login_attempts == 5
    assert user.locked_until is not None
    
    # Проверяем автоматическую разблокировку после истечения времени
    user.locked_until = datetime.utcnow() - timedelta(minutes=15)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    assert response.status_code == 200
    
    # Проверяем сброс счетчика попыток после успешного входа
    user = get_user_by_email(db_session, user_data["email"])
    assert user.login_attempts == 0
    assert user.locked_until is None 