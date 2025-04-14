from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError, jwt
from core.config import settings
from models.token import TokenBlacklist
from redis import Redis
from core.config import settings

redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def is_token_blacklisted(token: str) -> bool:
    return bool(redis.get(f"blacklist:{token}"))

def blacklist_token(token: str, expires_in: int) -> None:
    redis.setex(f"blacklist:{token}", expires_in, "1")

def revoke_token(token: str, db: Session) -> None:
    # Проверяем валидность токена
    try:
        payload = verify_token(token)
    except HTTPException:
        return
    
    # Получаем время истечения
    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.utcnow()
    
    # Добавляем токен в черный список на оставшееся время
    ttl = int((exp - now).total_seconds())
    if ttl > 0:
        blacklist_token(token, ttl)
        
    # Добавляем запись в БД для аудита
    db_token = TokenBlacklist(
        token=token,
        expires_at=exp,
        blacklisted_at=now
    )
    db.add(db_token)
    db.commit() 