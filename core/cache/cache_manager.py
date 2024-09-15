from functools import wraps
from typing import Any, Callable, Type

from .base import BaseBackend, BaseKeyMaker
from .cache_tag import CacheTag
from .custom_key_maker import CustomKeyMaker
from .redis_backend import RedisBackend


class CacheManager:
    def __init__(self):
        self.backend = None
        self.key_maker = None

    def init(self, backend: Type[BaseBackend], key_maker: Type[BaseKeyMaker]) -> None:
        self.backend = backend
        self.key_maker = key_maker

    def cached(
        self,
        prefix: str = None,
        tag: CacheTag = None,
        ttl: int = 60,
        filter_func: Callable[[Any], bool] = None,
    ):
        def _cached(function):
            @wraps(function)
            def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise ValueError("Backend or KeyMaker not initialized")

                key = self.key_maker.make(
                    function=function,
                    prefix=prefix if prefix else tag.value,
                )
                cached_response = self.backend.get(key=key)

                if cached_response:
                    # if filter_func:
                    #     filtered_items = []

                    return cached_response

                response = function(*args, **kwargs)
                self.backend.set(response=response, key=key, ttl=ttl)

                return response

            return __cached

        return _cached

    def remove_by_tag(self, tag: CacheTag) -> None:
        self.backend.delete_startswith(value=tag.value)

    def remove_by_prefix(self, prefix: str) -> None:
        self.backend.delete_startswith(value=prefix)

    def remove_by_key(self, key):
        self.backend.delete_by_key(key)

    def get_by_prefix(self, prefix, function: Callable[[Any], bool] = None) -> Any:
        key = self.key_maker.make(
            function=function if function else self.set_cache, prefix=prefix
        )

        response = self.backend.get(key)

        return response

    def set_cache(self, response, prefix: str):
        key = self.key_maker.make(function=self.set_cache, prefix=prefix)
        self.backend.set(response=response, key=key)


Cache = CacheManager()
