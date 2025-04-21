from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from sqlalchemy.orm import Session
from core.config import settings
from models.user import User
from schemas.token import TokenData
from services.user_service import UserService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по email и паролю
        """
        return self.user_service.authenticate_user(email, password)

    def create_access_token(self, user: User) -> str:
        """
        Создает JWT токен для пользователя
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user.id),
            "exp": expire,
            "email": user.email,
            "is_superuser": user.is_superuser
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Проверяет JWT токен и возвращает данные пользователя
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            is_superuser: bool = payload.get("is_superuser", False)
            if user_id is None or email is None:
                return None
            return TokenData(user_id=int(user_id), email=email, is_superuser=is_superuser)
        except jwt.JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """
        Получает текущего пользователя по токену
        """
        token_data = self.verify_token(token)
        if not token_data:
            return None
        return self.user_service.get_user(token_data.user_id)

    def get_current_active_user(self, token: str) -> Optional[User]:
        """
        Получает текущего активного пользователя по токену
        """
        current_user = self.get_current_user(token)
        if not current_user or not current_user.is_active:
            return None
        return current_user

    def get_current_superuser(self, token: str) -> Optional[User]:
        """
        Получает текущего суперпользователя по токену
        """
        current_user = self.get_current_user(token)
        if not current_user or not current_user.is_superuser:
            return None
        return current_user 