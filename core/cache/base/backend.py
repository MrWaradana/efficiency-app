from abc import ABC, abstractmethod
from typing import Any


class BaseBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Any: ...

    @abstractmethod
    def set(self, response: Any, key: str, ttl: int = 60) -> None: ...

    @abstractmethod
    def delete_startswith(self, value: str) -> None: ...
