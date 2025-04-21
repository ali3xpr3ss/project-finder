from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from models.notification import Notification
from api.services.notification_service import NotificationService
from api.services.cache_service import CacheService
from api.services.matching_service import MatchingService
from api.deps import get_db
from api.services.user_service import get_current_user

router = APIRouter()

def get_notification_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationService:
    cache_service = CacheService()
    matching_service = MatchingService(db)
    return NotificationService(db, cache_service, matching_service)

@router.get("/notifications", response_model=List[Dict[str, Any]])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> List[Dict[str, Any]]:
    """
    Получает все уведомления текущего пользователя
    """
    notifications = notification_service.get_user_notifications(current_user.id)
    return [notification.dict() for notification in notifications]

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    """
    Отмечает уведомление как прочитанное
    """
    notification = notification_service.mark_as_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return notification.dict()

@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> Dict[str, str]:
    """
    Отмечает все уведомления пользователя как прочитанные
    """
    notification_service.mark_all_as_read(current_user.id)
    return {"message": "Все уведомления отмечены как прочитанные"} 