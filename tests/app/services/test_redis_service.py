from unittest.mock import patch
from src.services import redis_service

@patch("app.services.redis_service.redis_client")
def test_cache_item_success(mock_redis):
    mock_redis.set.return_value = True
    result = redis_service.cache_item("key", "value")
    assert result is True
    mock_redis.set.assert_called_once_with("key", "value")

@patch("app.services.redis_service.redis_client")
def test_get_cached_item_success(mock_redis):
    mock_redis.get.return_value = "value"
    result = redis_service.get_cached_item("key")
    assert result == "value"
    mock_redis.get.assert_called_once_with("key")
