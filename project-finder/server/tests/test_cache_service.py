import pytest
from unittest.mock import Mock, patch
from services.cache_service import CacheService
from typing import Any, Dict

@pytest.fixture
def redis_mock() -> Mock:
    return Mock()

@pytest.fixture
def cache_service(redis_mock: Mock) -> CacheService:
    return CacheService(redis_client=redis_mock)

def test_get(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    key = "test_key"
    expected_value = "test_value"
    redis_mock.get.return_value = expected_value.encode()

    # Act
    result = cache_service.get(key)

    # Assert
    assert result == expected_value
    redis_mock.get.assert_called_once_with(key)

def test_get_not_found(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    key = "non_existent_key"
    redis_mock.get.return_value = None

    # Act
    result = cache_service.get(key)

    # Assert
    assert result is None
    redis_mock.get.assert_called_once_with(key)

def test_set(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    key = "test_key"
    value = "test_value"
    expire = 3600

    # Act
    cache_service.set(key, value, expire)

    # Assert
    redis_mock.set.assert_called_once_with(key, value, ex=expire)

def test_delete(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    key = "test_key"

    # Act
    cache_service.delete(key)

    # Assert
    redis_mock.delete.assert_called_once_with(key)

def test_clear_pattern(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    pattern = "test_*"
    keys = [b"test_1", b"test_2", b"test_3"]
    redis_mock.keys.return_value = keys

    # Act
    cache_service.clear_pattern(pattern)

    # Assert
    redis_mock.keys.assert_called_once_with(pattern)
    redis_mock.delete.assert_called_once_with(*keys)

def test_exists(cache_service: CacheService, redis_mock: Mock) -> None:
    # Arrange
    key = "test_key"
    redis_mock.exists.return_value = 1

    # Act
    result = cache_service.exists(key)

    # Assert
    assert result is True
    redis_mock.exists.assert_called_once_with(key)

def test_cache_set_get():
    """Тест сохранения и получения данных из кэша"""
    # Тестовые данные
    test_key = "test:key"
    test_data = {"name": "Test", "value": 123}
    
    # Сохраняем данные
    assert cache_service.set(test_key, test_data)
    
    # Получаем данные
    cached_data = cache_service.get(test_key)
    assert cached_data == test_data
    
    # Очищаем тестовые данные
    cache_service.delete(test_key)

def test_cache_delete():
    """Тест удаления данных из кэша"""
    # Тестовые данные
    test_key = "test:delete"
    test_data = {"name": "Test Delete"}
    
    # Сохраняем данные
    cache_service.set(test_key, test_data)
    
    # Удаляем данные
    assert cache_service.delete(test_key)
    
    # Проверяем, что данные удалены
    assert cache_service.get(test_key) is None

def test_cache_clear_pattern():
    """Тест очистки кэша по паттерну"""
    # Тестовые данные
    test_keys = [
        "test:pattern:1",
        "test:pattern:2",
        "other:key"
    ]
    test_data = {"name": "Test Pattern"}
    
    # Сохраняем данные
    for key in test_keys:
        cache_service.set(key, test_data)
    
    # Очищаем по паттерну
    assert cache_service.clear_pattern("test:pattern:*")
    
    # Проверяем результаты
    assert cache_service.get("test:pattern:1") is None
    assert cache_service.get("test:pattern:2") is None
    assert cache_service.get("other:key") == test_data
    
    # Очищаем оставшиеся тестовые данные
    cache_service.delete("other:key")

def test_cache_expiration():
    """Тест истечения срока действия кэша"""
    # Тестовые данные
    test_key = "test:expiration"
    test_data = {"name": "Test Expiration"}
    
    # Сохраняем данные с коротким сроком действия
    assert cache_service.set(test_key, test_data, expire_seconds=1)
    
    # Проверяем, что данные доступны
    assert cache_service.get(test_key) == test_data
    
    # Ждем истечения срока
    import time
    time.sleep(2)
    
    # Проверяем, что данные удалены
    assert cache_service.get(test_key) is None

def test_cache_invalid_data():
    """Тест обработки некорректных данных"""
    # Тестовые данные
    test_key = "test:invalid"
    test_data = {"name": "Test Invalid"}
    
    # Сохраняем данные
    assert cache_service.set(test_key, test_data)
    
    # Проверяем получение несуществующего ключа
    assert cache_service.get("nonexistent:key") is None
    
    # Проверяем удаление несуществующего ключа
    assert cache_service.delete("nonexistent:key")
    
    # Очищаем тестовые данные
    cache_service.delete(test_key) 