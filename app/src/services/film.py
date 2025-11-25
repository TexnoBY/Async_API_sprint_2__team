from typing import List, Optional

from src.models.film import FilmList, FilmDitail
from src.services.interfaces import FilmRepositoryInterface


class FilmService:
    def __init__(self, film_repository: FilmRepositoryInterface):
        self._film_repo = film_repository

    async def get_by_id(self, film_id: str) -> Optional[FilmDitail]:
        return await self._film_repo.get_by_id(film_id)

    async def get_sorted_list(self, sort_field: str, sort_order: str = "asc",
                              page: int = 0, page_size: int = 10, **kwargs) -> Optional[List[FilmList]]:
        genres = kwargs.get('genres')
        films = await self._film_repo.get_sorted(
            sort_field, sort_order, page, page_size, genres=genres
        )
        return films if films else None

    async def search(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[FilmList]]:
        films = await self._film_repo.search(query, page, page_size)
        return films if films else None

    async def get_sort_list_by_param(self, sort_field: str, sort_order: str = "asc",
                                     page: int = 0, page_size: int = 10, genres: str = "") -> Optional[List[FilmList]]:
        films = await self._film_repo.get_sorted(
            sort_field, sort_order, page, page_size, genres=genres
        )
        return films if films else None

    async def get_search_list(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[FilmList]]:
        films = await self._film_repo.search(query, page, page_size)
        return films if films else None


def get_film_service() -> FilmService:
    """Factory function for FilmService dependency injection"""
    from src.repositories.film_repository import FilmRepository
    from src.db.elastic import get_elastic_client

    # This is a simplified version - in real implementation you'd use proper DI
    elastic_client = get_elastic_client()
    film_repository = FilmRepository(elastic_client)
    return FilmService(film_repository)
