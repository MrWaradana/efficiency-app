import logging
import pickle
from typing import Any

import redis
import ujson

from core.cache.base import BaseBackend
from core.config import config

redis = redis.Redis.from_url(config.REDIS_URL)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class RedisBackend(BaseBackend):
    def get(self, key: str) -> Any:
        result = redis.get(key)
        if not result:
            return

        try:
            return ujson.loads(result.decode("utf8"))
        except (UnicodeDecodeError, ujson.JSONDecodeError) as e:
            logger.error(f"JSON decode error for key '{key}': {e}")
            # Try to deserialize using pickle
            try:
                return pickle.loads(result)
            except (pickle.UnpicklingError, EOFError, AttributeError) as e:
                logger.error(f"Pickle load error for key '{key}': {e}")
                return None

    def set(self, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, dict):
            response = ujson.dumps(response)
        elif isinstance(response, object):
            response = pickle.dumps(response)

        redis.set(name=key, value=response, ex=ttl)

    def delete_startswith(self, value: str) -> None:
        for key in redis.scan_iter(f"{value}::*"):
            redis.delete(key)

    def delete_by_key(self, value: str) -> None:
        redis.delete(value)
