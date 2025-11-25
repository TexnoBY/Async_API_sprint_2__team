from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """Базовый интерфейс для всех репозиториев"""

    @abstractmethod
    async def get_by_id(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Получить документ по ID"""
        pass

    @abstractmethod
    async def search(self, index: str, body: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск документов"""
        pass

    @abstractmethod
    async def exists(self, index: str, doc_id: str) -> bool:
        """Проверить существование документа"""
        pass
