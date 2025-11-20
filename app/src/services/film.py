from functools import lru_cache
from typing import List, Optional

from fastapi import Depends
from src.repositories.film_repository import FilmRepository
from src.models.film import FilmList, FilmDitail


class FilmService:
    def __init__(self, film_repository: FilmRepository):
        self.film_repo = film_repository

    async def get_by_id(self, film_id: str) -> Optional[FilmDitail]:
        return await self.film_repo.get_film_by_id(film_id)

    async def get_sort_list_by_param(self, sort_field: str,
                                     sort_order: str = "asc",
                                     page: int = 0, page_size: int = 10,
                                     genres: str | None = None) -> Optional[List[FilmList]]:
        films = await self.film_repo.get_sorted_films(
            sort_field, sort_order, page, page_size, genres
        )
        return films if films else None

    async def get_search_list(self, query: str, page: int = 0,
                              page_size: int = 10) -> Optional[List[FilmList]]:
        films = await self.film_repo.search_films(query, page, page_size)
        return films if films else None


@lru_cache()
def get_film_service(
        film_repository: FilmRepository = Depends(FilmRepository),
) -> FilmService:
    return FilmService(film_repository)
