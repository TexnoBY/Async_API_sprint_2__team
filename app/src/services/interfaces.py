from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Any

T = TypeVar('T')
ID = TypeVar('ID')

# Import models for type hints
from src.models.genre import GenreDitail, GenreList


class BaseRepository(Generic[T, ID], ABC):
    """Базовый интерфейс для всех репозиториев"""

    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Получить сущность по ID"""
        pass


class SearchableRepository(BaseRepository[T, ID], ABC):
    """Интерфейс для репозиториев с поиском"""

    @abstractmethod
    async def search(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[T]]:
        """Поиск сущностей"""
        pass


class SortableRepository(BaseRepository[T, ID], ABC):
    """Интерфейс для репозиториев с сортировкой"""

    @abstractmethod
    async def get_sorted(self, sort_field: str, sort_order: str = "asc",
                         page: int = 0, page_size: int = 10, **kwargs) -> Optional[List[T]]:
        """Получить отсортированный список"""
        pass


class FilmRepositoryInterface(SearchableRepository, SortableRepository, ABC):
    """Интерфейс для репозитория фильмов"""
    pass


class GenreRepositoryInterface(BaseRepository[GenreDitail, str], ABC):
    """Интерфейс для репозитория жанров"""

    @abstractmethod
    async def get_all(self) -> Optional[List[GenreList]]:
        """Получить все жанры"""
        pass


class PersonRepositoryInterface(SearchableRepository, ABC):
    """Интерфейс для репозитория персон"""

    @abstractmethod
    async def get_films_by_person(self, person_id: ID) -> Optional[List[Any]]:
        """Получить фильмы по персоне"""
        pass
