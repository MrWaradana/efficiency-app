from functools import wraps
from typing import Any, Callable, Type

from .base import BaseBackend, BaseKeyMaker
from .cache_tag import CacheTag
from .redis_backend import RedisBackend
from .custom_key_maker import CustomKeyMaker


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
            async def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise ValueError("Backend or KeyMaker not initialized")

                key = await self.key_maker.make(
                    function=function,
                    prefix=prefix if prefix else tag.value,
                )
                cached_response = await self.backend.get(key=key)
                if cached_response:
                    # if filter_func:
                    #     filtered_items = []

                    return cached_response

                response = await function(*args, **kwargs)
                await self.backend.set(response=response, key=key, ttl=ttl)
                return response

            return __cached

        return _cached

    async def remove_by_tag(self, tag: CacheTag) -> None:
        await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, prefix: str) -> None:
        await self.backend.delete_startswith(value=prefix)

    async def get_by_key(self, function, prefix):
        key = await self.key_maker.make(
            function=function,
            prefix=prefix
        )
        
        response = self.backend.get(key)
        
        return response


Cache = CacheManager()

