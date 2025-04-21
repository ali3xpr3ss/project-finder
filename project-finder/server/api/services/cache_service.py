from typing import Any, Optional
from datetime import datetime, timedelta

class CacheService:
    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Получает значение из кэша
        """
        if key not in self._cache:
            return None
        
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None
        
        return self._cache[key]

    def set(self, key: str, value: Any, expire_in: Optional[int] = None) -> None:
        """
        Устанавливает значение в кэш
        
        :param key: Ключ
        :param value: Значение
        :param expire_in: Время жизни в секундах
        """
        self._cache[key] = value
        if expire_in is not None:
            self._expiry[key] = datetime.now() + timedelta(seconds=expire_in)

    def delete(self, key: str) -> None:
        """
        Удаляет значение из кэша
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]

    def clear(self) -> None:
        """
        Очищает весь кэш
        """
        self._cache.clear()
        self._expiry.clear() 