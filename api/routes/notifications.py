from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.cache_service import CacheService
from services.matching_service import MatchingService
from services.notification_service import NotificationService
from models.user import User
from api.deps import get_current_user

router = APIRouter()

def get_notification_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationService:
    cache_service = CacheService()
    matching_service = MatchingService(db)
    return NotificationService(db, cache_service, matching_service)

@router.get("/notifications", response_model=List[Dict[str, Any]])
def get_notifications(
    notification_service: NotificationService = Depends(get_notification_service)
) -> List[Dict[str, Any]]:
    notifications = notification_service.get_user_notifications(notification_service.current_user.id)
    return [notification.dict() for notification in notifications]

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    notification = notification_service.mark_as_read(notification_id, notification_service.current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.post("/notifications/read-all")
def mark_all_notifications_read(
    notification_service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    notification_service.mark_all_as_read(notification_service.current_user.id)
    return {"message": "All notifications marked as read"} 