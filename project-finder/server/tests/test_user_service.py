import pytest
from sqlalchemy.orm import Session
from api.services.user_service import (
    create_user,
    get_user_by_email,
    authenticate_user,
    get_current_user
)
from schemas.user import UserCreate, UserUpdate
from models.user import User
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt
from core.config import settings
from core.security import verify_password

def test_create_user(db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    
    # Создаем пользователя
    user = create_user(db_session, user_data)
    
    # Проверяем, что пользователь создан
    assert user.email == user_data.email
    assert user.name == user_data.name
    assert user.role == user_data.role
    assert user.hashed_password != user_data.password  # Пароль должен быть захеширован
    
    # Проверяем валидацию email
    with pytest.raises(HTTPException) as exc_info:
        invalid_email_data = user_data.copy()
        invalid_email_data["email"] = "invalid-email"
        create_user(db_session, invalid_email_data)
    assert exc_info.value.status_code == 422
    assert "Invalid email format" in str(exc_info.value.detail)
    
    # Проверяем дублирование email
    with pytest.raises(HTTPException) as exc_info:
        create_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)
    
    # Проверяем минимальную длину имени
    with pytest.raises(HTTPException) as exc_info:
        short_name_data = user_data.copy()
        short_name_data["email"] = "test2@example.com"
        short_name_data["name"] = "T"  # Слишком короткое имя
        create_user(db_session, short_name_data)
    assert exc_info.value.status_code == 400
    assert "Name must be at least 2 characters long" in str(exc_info.value.detail)
    
    # Проверяем максимальную длину имени
    with pytest.raises(HTTPException) as exc_info:
        long_name_data = user_data.copy()
        long_name_data["email"] = "test3@example.com"
        long_name_data["name"] = "T" * 101  # Слишком длинное имя
        create_user(db_session, long_name_data)
    assert exc_info.value.status_code == 400
    assert "Name must not exceed 100 characters" in str(exc_info.value.detail)
    
    # Проверяем валидацию роли
    with pytest.raises(HTTPException) as exc_info:
        invalid_role_data = user_data.copy()
        invalid_role_data["email"] = "test4@example.com"
        invalid_role_data["role"] = "invalid_role"
        create_user(db_session, invalid_role_data)
    assert exc_info.value.status_code == 422
    assert "Invalid role" in str(exc_info.value.detail)
    
    # Проверяем специальные символы в имени
    with pytest.raises(HTTPException) as exc_info:
        special_chars_data = user_data.copy()
        special_chars_data["email"] = "test5@example.com"
        special_chars_data["name"] = "Test User!@#$%^&*()"
        create_user(db_session, special_chars_data)
    assert exc_info.value.status_code == 400
    assert "Name contains invalid characters" in str(exc_info.value.detail)
    
    # Проверяем пустые поля
    with pytest.raises(HTTPException) as exc_info:
        empty_data = UserCreate(
            email="",
            password="",
            name="",
            role=""
        )
        create_user(db_session, empty_data)
    assert exc_info.value.status_code == 422
    assert "field required" in str(exc_info.value.detail)

def test_get_user_by_email(db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    user = create_user(db_session, user_data)
    
    # Получаем пользователя по email
    found_user = get_user_by_email(db_session, user_data.email)
    
    # Проверяем, что пользователь найден
    assert found_user is not None
    assert found_user.email == user_data.email
    assert found_user.name == user_data.name
    
    # Проверяем несуществующий email
    non_existent_user = get_user_by_email(db_session, "nonexistent@example.com")
    assert non_existent_user is None
    
    # Проверяем неактивного пользователя
    user.is_active = False
    db_session.commit()
    
    found_user = get_user_by_email(db_session, user_data.email)
    assert found_user is not None
    assert not found_user.is_active
    
    # Проверяем пустой email
    with pytest.raises(HTTPException) as exc_info:
        get_user_by_email(db_session, "")
    assert exc_info.value.status_code == 400
    assert "Email cannot be empty" in str(exc_info.value.detail)
    
    # Проверяем неверный формат email
    with pytest.raises(HTTPException) as exc_info:
        get_user_by_email(db_session, "invalid-email")
    assert exc_info.value.status_code == 422
    assert "Invalid email format" in str(exc_info.value.detail)

def test_authenticate_user(db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    user = create_user(db_session, user_data)
    
    # Проверяем аутентификацию с правильными данными
    authenticated_user = authenticate_user(
        db_session, user_data.email, user_data.password
    )
    assert authenticated_user is not None
    assert authenticated_user.email == user_data.email
    
    # Проверяем аутентификацию с неправильным паролем
    wrong_password_user = authenticate_user(
        db_session, user_data.email, "wrongpassword"
    )
    assert wrong_password_user is None
    
    # Проверяем несуществующий email
    non_existent_user = authenticate_user(
        db_session, "nonexistent@example.com", "password"
    )
    assert non_existent_user is None
    
    # Проверяем неактивного пользователя
    user.is_active = False
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, user_data.email, user_data.password)
    assert exc_info.value.status_code == 403
    assert "User account is inactive" in str(exc_info.value.detail)
    
    # Проверяем блокировку аккаунта
    user.is_active = True
    user.login_attempts = 5
    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, user_data.email, user_data.password)
    assert exc_info.value.status_code == 403
    assert "Account is locked" in str(exc_info.value.detail)
    
    # Проверяем пустые поля
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, "", "")
    assert exc_info.value.status_code == 400
    assert "Email and password cannot be empty" in str(exc_info.value.detail)
    
    # Проверяем неверный формат email
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, "invalid-email", "password")
    assert exc_info.value.status_code == 422
    assert "Invalid email format" in str(exc_info.value.detail)

def test_get_current_user(db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    user = create_user(db_session, user_data)
    
    # Создаем тестовый токен
    token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access"
    }
    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    # Проверяем получение текущего пользователя
    current_user = get_current_user(db_session, token)
    assert current_user is not None
    assert current_user.email == user.email
    
    # Проверяем обработку неверного токена
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db_session, "invalid_token")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)
    
    # Проверяем неактивного пользователя
    user.is_active = False
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db_session, token)
    assert exc_info.value.status_code == 403
    assert "User account is inactive" in str(exc_info.value.detail)
    
    # Проверяем истекший токен
    expired_token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "type": "access"
    }
    expired_token = jwt.encode(expired_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db_session, expired_token)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in str(exc_info.value.detail)
    
    # Проверяем отсутствие токена
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db_session, "")
    assert exc_info.value.status_code == 401
    assert "Token is required" in str(exc_info.value.detail)
    
    # Проверяем неверный тип токена
    refresh_token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db_session, refresh_token)
    assert exc_info.value.status_code == 400
    assert "Invalid token type" in str(exc_info.value.detail)

def test_update_user(db_session: Session):
    # Создаем тестового пользователя
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User",
        role="user"
    )
    user = create_user(db_session, user_data)
    
    # Создаем админа
    admin_data = UserCreate(
        email="admin@example.com",
        password="AdminPassword123!",
        name="Admin User",
        role="admin"
    )
    admin = create_user(db_session, admin_data)
    
    # Проверяем успешное обновление с правами админа
    update_data = UserUpdate(
        name="Updated Name",
        role="admin",
        email="updated@example.com",
        password="NewPassword123!",
        is_active=True
    )
    updated_user = update_user(db_session, user.id, update_data, admin)
    
    assert updated_user.name == update_data.name
    assert updated_user.role == update_data.role
    assert updated_user.email == update_data.email
    assert updated_user.is_active == update_data.is_active
    assert verify_password(update_data.password, updated_user.hashed_password)
    
    # Проверяем обновление без прав админа
    user_update_data = UserUpdate(name="User Update")
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, admin.id, user_update_data, user)
    assert exc_info.value.status_code == 403
    assert "Only administrators can change user roles" in str(exc_info.value.detail)
    
    # Проверяем несуществующего пользователя
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, 999, user_update_data, admin)
    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)
    
    # Проверяем валидацию имени
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(name="A"), admin)
    assert exc_info.value.status_code == 400
    assert "Name must be at least 2 characters long" in str(exc_info.value.detail)
    
    # Проверяем валидацию роли
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(role="invalid_role"), admin)
    assert exc_info.value.status_code == 422
    assert "Invalid role" in str(exc_info.value.detail)
    
    # Проверяем валидацию email
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(email="invalid_email"), admin)
    assert exc_info.value.status_code == 422
    assert "Invalid email format" in str(exc_info.value.detail)
    
    # Проверяем дублирование email
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(email=admin.email), admin)
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)
    
    # Проверяем специальные символы в имени
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(name="Test@User"), admin)
    assert exc_info.value.status_code == 400
    assert "Name cannot contain special characters" in str(exc_info.value.detail)
    
    # Проверяем слабый пароль
    with pytest.raises(HTTPException) as exc_info:
        update_user(db_session, user.id, UserUpdate(password="weak"), admin)
    assert exc_info.value.status_code == 400
    assert "Password must be at least 8 characters long" in str(exc_info.value.detail)
    
    # Проверяем частичное обновление
    partial_update = UserUpdate(name="Partial Update")
    updated_user = update_user(db_session, user.id, partial_update, admin)
    assert updated_user.name == partial_update.name
    assert updated_user.email == update_data.email  # Не изменилось
    assert updated_user.role == update_data.role  # Не изменилось
    assert updated_user.is_active == update_data.is_active  # Не изменилось
    
    # Проверяем обновление статуса активности
    inactive_update = UserUpdate(is_active=False)
    updated_user = update_user(db_session, user.id, inactive_update, admin)
    assert updated_user.is_active is False
    
    # Проверяем обновление email
    new_email_update = UserUpdate(email="newemail@example.com")
    updated_user = update_user(db_session, user.id, new_email_update, admin)
    assert updated_user.email == "newemail@example.com"
    
    # Проверяем обновление пароля
    new_password_update = UserUpdate(password="NewSecurePassword123!")
    updated_user = update_user(db_session, user.id, new_password_update, admin)
    assert verify_password("NewSecurePassword123!", updated_user.hashed_password) 