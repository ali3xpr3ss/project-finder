from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получение пользователя по email
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получение списка пользователей
        """
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: UserCreate) -> User:
        """
        Создание нового пользователя
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            skills=user.skills,
            experience=user.experience,
            languages=user.languages,
            description=user.description
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Обновление данных пользователя
        """
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя
        """
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        self.db.delete(db_user)
        self.db.commit()
        return True

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Деактивация пользователя
        """
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def activate_user(self, user_id: int) -> Optional[User]:
        """
        Активация пользователя
        """
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_skills(self) -> List[str]:
        """
        Получение списка всех навыков пользователей
        """
        all_skills: List[str] = []
        users = self.get_users()
        for user in users:
            if user.skills:
                all_skills.extend(user.skills)
        return list(set(all_skills))

    def get_user_roles(self) -> List[str]:
        """
        Получение списка всех ролей пользователей
        """
        return list(set(user.role for user in self.get_users()))

    def get_user_languages(self) -> List[str]:
        """
        Получение списка всех языков пользователей
        """
        all_languages: List[str] = []
        users = self.get_users()
        for user in users:
            if user.languages:
                all_languages.extend(user.languages)
        return list(set(all_languages)) 