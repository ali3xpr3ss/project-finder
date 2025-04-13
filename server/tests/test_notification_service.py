import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from models.notification import Notification
from models.user import User
from models.project import Project
from services.notification_service import NotificationService

def test_create_notification(db: Session):
    """Тест создания уведомления"""
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="test_password"
    )
    db.add(user)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Создаем уведомление
    notification = notification_service.create_notification(
        user_id=user.id,
        title="Test Notification",
        message="Test Message",
        notification_type="test"
    )
    
    # Проверяем результат
    assert notification.user_id == user.id
    assert notification.title == "Test Notification"
    assert notification.message == "Test Message"
    assert notification.notification_type == "test"
    assert notification.is_read == False
    assert notification.created_at is not None
    
    # Очищаем тестовые данные
    db.delete(notification)
    db.delete(user)
    db.commit()

def test_get_user_notifications(db: Session):
    """Тест получения уведомлений пользователя"""
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="test_password"
    )
    db.add(user)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Создаем несколько уведомлений
    notifications = []
    for i in range(5):
        notification = notification_service.create_notification(
            user_id=user.id,
            title=f"Test Notification {i}",
            message=f"Test Message {i}",
            notification_type="test"
        )
        notifications.append(notification)
    
    # Получаем уведомления
    user_notifications = notification_service.get_user_notifications(user.id)
    
    # Проверяем результат
    assert len(user_notifications) == 5
    assert all(n.user_id == user.id for n in user_notifications)
    
    # Очищаем тестовые данные
    for notification in notifications:
        db.delete(notification)
    db.delete(user)
    db.commit()

def test_mark_as_read(db: Session):
    """Тест отметки уведомления как прочитанного"""
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="test_password"
    )
    db.add(user)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Создаем уведомление
    notification = notification_service.create_notification(
        user_id=user.id,
        title="Test Notification",
        message="Test Message",
        notification_type="test"
    )
    
    # Отмечаем как прочитанное
    updated_notification = notification_service.mark_as_read(notification.id, user.id)
    
    # Проверяем результат
    assert updated_notification.is_read == True
    assert updated_notification.read_at is not None
    
    # Очищаем тестовые данные
    db.delete(notification)
    db.delete(user)
    db.commit()

def test_mark_all_as_read(db: Session):
    """Тест отметки всех уведомлений как прочитанных"""
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="test_password"
    )
    db.add(user)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Создаем несколько непрочитанных уведомлений
    notifications = []
    for i in range(3):
        notification = notification_service.create_notification(
            user_id=user.id,
            title=f"Test Notification {i}",
            message=f"Test Message {i}",
            notification_type="test"
        )
        notifications.append(notification)
    
    # Отмечаем все как прочитанные
    assert notification_service.mark_all_as_read(user.id)
    
    # Проверяем результат
    user_notifications = notification_service.get_user_notifications(user.id)
    assert all(n.is_read == True for n in user_notifications)
    assert all(n.read_at is not None for n in user_notifications)
    
    # Очищаем тестовые данные
    for notification in notifications:
        db.delete(notification)
    db.delete(user)
    db.commit()

def test_check_new_matches(db: Session):
    """Тест проверки новых совпадений"""
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="test_password",
        technologies=["Python", "FastAPI"],
        roles=["developer"]
    )
    db.add(user)
    db.commit()
    
    # Создаем тестовый проект
    project = Project(
        name="Test Project",
        description="Test Description",
        technologies=["Python", "FastAPI"],
        required_roles=["developer"],
        status="active",
        user_id=user.id
    )
    db.add(project)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Проверяем новые совпадения
    notifications = notification_service.check_new_matches(user)
    
    # Проверяем результат
    assert isinstance(notifications, list)
    
    # Очищаем тестовые данные
    db.delete(project)
    db.delete(user)
    db.commit()

def test_check_project_matches(db: Session):
    """Тест проверки новых подходящих участников для проекта"""
    # Создаем тестового пользователя (владелец проекта)
    project_owner = User(
        email="owner@example.com",
        name="Project Owner",
        hashed_password="test_password"
    )
    db.add(project_owner)
    db.commit()
    
    # Создаем тестовый проект
    project = Project(
        name="Test Project",
        description="Test Description",
        technologies=["Python", "FastAPI"],
        required_roles=["developer"],
        status="active",
        user_id=project_owner.id
    )
    db.add(project)
    db.commit()
    
    # Создаем сервис уведомлений
    notification_service = NotificationService(db)
    
    # Проверяем новые совпадения
    notifications = notification_service.check_project_matches(project)
    
    # Проверяем результат
    assert isinstance(notifications, list)
    
    # Очищаем тестовые данные
    db.delete(project)
    db.delete(project_owner)
    db.commit() 