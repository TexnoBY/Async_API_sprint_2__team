from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')
ID = TypeVar('ID')


class BaseService(Generic[T, ID], ABC):
    """Базовый интерфейс для всех сервисов"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Получить сущность по ID"""
        pass


class SearchableService(BaseService[T, ID], ABC):
    """Интерфейс для сервисов с поиском"""
    
    @abstractmethod
    async def search(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[T]]:
        """Поиск сущностей"""
        pass


class SortableService(BaseService[T, ID], ABC):
    """Интерфейс для сервисов с сортировкой"""
    
    @abstractmethod
    async def get_sorted_list(self, sort_field: str, sort_order: str = "asc",
                             page: int = 0, page_size: int = 10, **kwargs) -> Optional[List[T]]:
        """Получить отсортированный список"""
        pass