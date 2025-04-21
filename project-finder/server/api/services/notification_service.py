from typing import List, Optional
from sqlalchemy.orm import Session
from models.notification import Notification
from models.user import User
from .cache_service import CacheService
from .matching_service import MatchingService

class NotificationService:
    def __init__(
        self,
        db: Session,
        cache_service: CacheService,
        matching_service: MatchingService
    ):
        self.db = db
        self.cache_service = cache_service
        self.matching_service = matching_service

    def get_user_notifications(self, user_id: int) -> List[Notification]:
        """
        Получает все уведомления пользователя
        """
        cache_key = f"user_notifications_{user_id}"
        cached = self.cache_service.get(cache_key)
        if cached is not None:
            return cached

        notifications = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        
        self.cache_service.set(cache_key, notifications, expire_in=300)  # 5 минут
        return notifications

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """
        Отмечает уведомление как прочитанное
        """
        notification = (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
            .first()
        )
        
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
            
            # Инвалидируем кэш
            self.cache_service.delete(f"user_notifications_{user_id}")
        
        return notification

    def mark_all_as_read(self, user_id: int) -> None:
        """
        Отмечает все уведомления пользователя как прочитанные
        """
        (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .update({"is_read": True})
        )
        self.db.commit()
        
        # Инвалидируем кэш
        self.cache_service.delete(f"user_notifications_{user_id}")

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        type: str = "info"
    ) -> Notification:
        """
        Создает новое уведомление
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Инвалидируем кэш
        self.cache_service.delete(f"user_notifications_{user_id}")
        
        return notification 