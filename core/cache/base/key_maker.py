from abc import ABC, abstractmethod
from typing import Callable


class BaseKeyMaker(ABC):
    @abstractmethod
    def make(self, function: Callable, prefix: str) -> str: ...
