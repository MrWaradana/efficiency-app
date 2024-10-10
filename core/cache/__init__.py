from .cache_manager import Cache
from .cache_tag import CacheTag
from .custom_key_maker import CustomKeyMaker
from .redis_backend import RedisBackend
from flask_caching import Cache as flask_cache

cache_flask = flask_cache()

__all__ = [
    "Cache",
    "RedisBackend",
    "CustomKeyMaker",
    "CacheTag",
]
