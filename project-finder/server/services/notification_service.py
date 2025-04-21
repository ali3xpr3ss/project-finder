from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.notification import Notification
from models.user import User
from models.project import Project
from services.cache_service import CacheService
from services.matching_service import MatchingService

class NotificationService:
    def __init__(self, db: Session, cache_service: CacheService, matching_service: MatchingService) -> None:
        self.db = db
        self.cache_service = cache_service
        self.matching_service = matching_service
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        related_id: Optional[int] = None
    ) -> Notification:
        """Создает новое уведомление"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_id=related_id,
            is_read=False,
            created_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_user_notifications(self, user_id: int) -> List[Notification]:
        """Получает все уведомления пользователя"""
        return self.db.query(Notification).filter(Notification.user_id == user_id).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Отмечает уведомление как прочитанное"""
        notification = self.db.query(Notification)\
            .filter(Notification.id == notification_id, Notification.user_id == user_id)\
            .first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, user_id: int) -> None:
        """Отмечает все уведомления пользователя как прочитанные"""
        notifications = self.db.query(Notification)\
            .filter(Notification.user_id == user_id, Notification.is_read == False)\
            .all()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        self.db.commit()
    
    def check_new_matches(self) -> None:
        """Проверяет новые совпадения и создает уведомления"""
        # Получаем текущие совпадения
        current_matches = self.matching_service.find_all_matches()
        
        # Получаем предыдущие совпадения из кэша
        cached_matches = self.cache_service.get("previous_matches")
        
        if cached_matches is None:
            # Если кэш пуст, сохраняем текущие совпадения
            self.cache_service.set("previous_matches", str(current_matches), expire=3600)
            return
        
        # Сравниваем текущие совпадения с предыдущими
        for match in current_matches:
            if str(match) not in cached_matches:
                # Создаем уведомление о новом совпадении
                self.create_notification(
                    user_id=match["user_id"],
                    title="Новое совпадение",
                    message=f"Найдено новое совпадение с проектом {match['project_title']}",
                    notification_type="match"
                )
        
        # Обновляем кэш
        self.cache_service.set("previous_matches", str(current_matches), expire=3600)
    
    def check_project_matches(self) -> None:
        """Проверяет совпадения для всех проектов"""
        # Получаем текущие совпадения проектов
        current_matches = self.matching_service.find_project_matches()
        
        # Получаем предыдущие совпадения из кэша
        cached_matches = self.cache_service.get("previous_project_matches")
        
        if cached_matches is None:
            # Если кэш пуст, сохраняем текущие совпадения
            self.cache_service.set("previous_project_matches", str(current_matches), expire=3600)
            return
        
        # Сравниваем текущие совпадения с предыдущими
        for match in current_matches:
            if str(match) not in cached_matches:
                # Создаем уведомление о новом совпадении проекта
                self.create_notification(
                    user_id=match["user_id"],
                    title="Новый проект",
                    message=f"Найден новый подходящий проект: {match['project_title']}",
                    notification_type="project_match",
                    related_id=match["project_id"]
                )
        
        # Обновляем кэш
        self.cache_service.set("previous_project_matches", str(current_matches), expire=3600) 