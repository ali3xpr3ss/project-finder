from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import verify_password, get_password_hash
from core.config import settings

class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверяем, не существует ли уже пользователь с таким email
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Создаем нового пользователя
        db_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            name=user_data.name,
            role=user_data.role,
            is_active=True,
            login_attempts=0,
            locked_until=None,
            full_name=user_data.full_name,
            skills=user_data.skills,
            experience=user_data.experience,
            languages=user_data.languages,
            description=user_data.description
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Проверяем, не заблокирован ли аккаунт
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked"
            )
        
        # Проверяем пароль
        if not verify_password(password, user.hashed_password):
            # Увеличиваем счетчик попыток
            user.login_attempts += 1
            
            # Если превышен лимит попыток, блокируем аккаунт
            if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is locked"
                )
            
            self.db.commit()
            return None
        
        # Сбрасываем счетчик попыток при успешном входе
        user.login_attempts = 0
        user.locked_until = None
        self.db.commit()
        
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновление информации о пользователе"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Проверяем права на изменение роли
        if user_data.role and user_data.role != user.role:
            if current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only administrators can change user roles"
                )
        
        # Обновляем данные
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: int, current_user: User) -> User:
        """Деактивация пользователя"""
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can deactivate users"
            )
        
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

    def activate_user(self, user_id: int, current_user: User) -> User:
        """Активация пользователя"""
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can activate users"
            )
        
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        user.login_attempts = 0
        user.locked_until = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def search_users(
        self,
        query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        experience: Optional[int] = None,
        role: Optional[str] = None
    ) -> List[User]:
        filters = []
        if query:
            filters.append(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.description.ilike(f"%{query}%")
                )
            )
        if skills:
            filters.extend([User.skills.contains([skill]) for skill in skills])
        if experience is not None:
            filters.append(User.experience >= experience)
        if role:
            filters.append(User.role == role)

        if filters:
            return self.db.query(User).filter(*filters).all()
        return self.db.query(User).all()

    def get_user_stats(self) -> Dict[str, Any]:
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        all_skills = []
        for user in self.db.query(User).all():
            all_skills.extend(user.skills)
        skill_counts = {}
        for skill in set(all_skills):
            skill_counts[skill] = all_skills.count(skill)
        
        all_roles = [user.role for user in self.db.query(User).all()]
        role_counts = {}
        for role in set(all_roles):
            role_counts[role] = all_roles.count(role)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "skill_distribution": skill_counts,
            "role_distribution": role_counts
        } 