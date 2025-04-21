from typing import Optional, Any
from redis import Redis

class CacheService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def get(self, key: str) -> Optional[str]:
        """
        Получает значение из кэша по ключу
        """
        value = self.redis.get(key)
        if value is not None:
            return value.decode('utf-8')
        return None

    def set(self, key: str, value: str, expire: int = 3600) -> None:
        """
        Устанавливает значение в кэш с опциональным временем истечения
        """
        self.redis.set(key, value, ex=expire)

    def delete(self, key: str) -> None:
        """
        Удаляет значение из кэша по ключу
        """
        self.redis.delete(key)

    def clear_pattern(self, pattern: str) -> None:
        """
        Удаляет все ключи, соответствующие шаблону
        """
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def exists(self, key: str) -> bool:
        """
        Проверяет существование ключа в кэше
        """
        return bool(self.redis.exists(key))

# Создаем глобальный экземпляр сервиса кэширования
cache_service = CacheService() 