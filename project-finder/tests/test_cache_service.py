import pytest
from unittest.mock import Mock, patch
from services.cache_service import CacheService

@pytest.fixture
def redis_mock() -> Mock:
    return Mock()

@pytest.fixture
def cache_service(redis_mock: Mock) -> CacheService:
    with patch('redis.Redis', return_value=redis_mock):
        service = CacheService()
        return service

def test_set_success(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    value = "test_value"
    redis_mock.set.return_value = True
    
    result = cache_service.set(key, value)
    
    assert result is True
    redis_mock.set.assert_called_once_with(key, value, ex=None)

def test_set_with_expiry(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    value = "test_value"
    expire = 3600
    redis_mock.set.return_value = True
    
    result = cache_service.set(key, value, expire)
    
    assert result is True
    redis_mock.set.assert_called_once_with(key, value, ex=expire)

def test_set_failure(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    value = "test_value"
    redis_mock.set.side_effect = Exception("Redis error")
    
    result = cache_service.set(key, value)
    
    assert result is False

def test_get_success(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    expected_value = "test_value"
    redis_mock.get.return_value = expected_value
    
    result = cache_service.get(key)
    
    assert result == expected_value
    redis_mock.get.assert_called_once_with(key)

def test_get_missing_key(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.get.return_value = None
    
    result = cache_service.get(key)
    
    assert result is None
    redis_mock.get.assert_called_once_with(key)

def test_get_failure(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.get.side_effect = Exception("Redis error")
    
    result = cache_service.get(key)
    
    assert result is None

def test_delete_success(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.delete.return_value = 1
    
    result = cache_service.delete(key)
    
    assert result is True
    redis_mock.delete.assert_called_once_with(key)

def test_delete_failure(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.delete.side_effect = Exception("Redis error")
    
    result = cache_service.delete(key)
    
    assert result is False

def test_clear_pattern_success(cache_service: CacheService, redis_mock: Mock) -> None:
    pattern = "test_*"
    keys = ["test_1", "test_2", "test_3"]
    redis_mock.keys.return_value = keys
    redis_mock.delete.return_value = len(keys)
    
    result = cache_service.clear_pattern(pattern)
    
    assert result is True
    redis_mock.keys.assert_called_once_with(pattern)
    redis_mock.delete.assert_called_once_with(*keys)

def test_clear_pattern_no_keys(cache_service: CacheService, redis_mock: Mock) -> None:
    pattern = "test_*"
    redis_mock.keys.return_value = []
    
    result = cache_service.clear_pattern(pattern)
    
    assert result is True
    redis_mock.keys.assert_called_once_with(pattern)
    redis_mock.delete.assert_not_called()

def test_clear_pattern_failure(cache_service: CacheService, redis_mock: Mock) -> None:
    pattern = "test_*"
    redis_mock.keys.side_effect = Exception("Redis error")
    
    result = cache_service.clear_pattern(pattern)
    
    assert result is False

def test_exists_success(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.exists.return_value = 1
    
    result = cache_service.exists(key)
    
    assert result is True
    redis_mock.exists.assert_called_once_with(key)

def test_exists_failure(cache_service: CacheService, redis_mock: Mock) -> None:
    key = "test_key"
    redis_mock.exists.side_effect = Exception("Redis error")
    
    result = cache_service.exists(key)
    
    assert result is False 