from typing import Optional, Any
import redis
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self) -> None:
        try:
            self.redis = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                decode_responses=True
            )
            logger.info("Successfully connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """
        Получает значение из кэша по ключу
        """
        try:
            value = self.redis.get(key)
            if value is None:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except redis.RedisError as e:
            logger.error(f"Error getting value for key {key}: {e}")
            return None

    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Устанавливает значение в кэш с опциональным временем жизни
        """
        try:
            self.redis.set(key, value, ex=expire)
            logger.debug(f"Set cache for key: {key}")
            return True
        except redis.RedisError as e:
            logger.error(f"Error setting value for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Удаляет значение из кэша по ключу
        """
        try:
            result = self.redis.delete(key)
            if result > 0:
                logger.debug(f"Deleted cache for key: {key}")
            return result > 0
        except redis.RedisError as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> bool:
        """
        Удаляет все ключи, соответствующие шаблону
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.debug(f"Cleared keys matching pattern: {pattern}")
                return True
            return False
        except redis.RedisError as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Проверяет существование ключа в кэше
        """
        try:
            return bool(self.redis.exists(key))
        except redis.RedisError as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False 