from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.notification import Notification
from services.cache_service import CacheService
from services.matching_service import MatchingService
import json

class NotificationService:
    def __init__(self, db: Session, cache_service: CacheService, matching_service: MatchingService) -> None:
        self.db = db
        self.cache_service = cache_service
        self.matching_service = matching_service

    def create_notification(self, user_id: int, title: str, message: str, notification_type: str, related_id: Optional[int] = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_id=related_id,
            is_read=False
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: int) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.user_id == user_id).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
        return notification

    def mark_all_as_read(self, user_id: int) -> None:
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        self.db.commit()

    def check_new_matches(self, user_id: int) -> None:
        current_matches = self.matching_service.find_matching_profiles(user_id)
        cached_matches = self.cache_service.get(f"user_matches:{user_id}")
        if cached_matches:
            cached_matches = json.loads(cached_matches)
            new_matches = [match for match in current_matches if match["id"] not in cached_matches]
            for match in new_matches:
                self.create_notification(
                    user_id=user_id,
                    title="New Match Found",
                    message=f"You have a new match with {match['full_name']}",
                    notification_type="match",
                    related_id=match["id"]
                )
        self.cache_service.set(f"user_matches:{user_id}", json.dumps([m["id"] for m in current_matches]))

    def check_project_matches(self, project_id: int) -> None:
        current_matches = self.matching_service.find_matching_projects(project_id)
        cached_matches = self.cache_service.get(f"project_matches:{project_id}")
        if cached_matches:
            cached_matches = json.loads(cached_matches)
            new_matches = [match for match in current_matches if match["id"] not in cached_matches]
            for match in new_matches:
                self.create_notification(
                    user_id=match["id"],
                    title="New Project Match",
                    message=f"You have a new project match with {match['title']}",
                    notification_type="project_match",
                    related_id=project_id
                )
        self.cache_service.set(f"project_matches:{project_id}", json.dumps([m["id"] for m in current_matches])) 