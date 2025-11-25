from abc import ABC, abstractmethod
from typing import Any


class CacheKeyGenerator(ABC):
    @abstractmethod
    async def generate_key(self, endpoint: str, params: dict[str, Any]) -> str:
        pass
