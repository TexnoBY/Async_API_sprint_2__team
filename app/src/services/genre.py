from functools import lru_cache
from typing import List, Optional

from fastapi import Depends
from src.repositories.genre_repository import GenreRepository
from src.models.genre import GenreList, GenreDitail


class GenreService:
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repo = genre_repository

    async def get_by_id(self, genre_id: str) -> Optional[GenreDitail]:
        return await self.genre_repo.get_genre_by_id(genre_id)

    async def get_all_genres(self) -> Optional[List[GenreList]]:
        genres = await self.genre_repo.get_all_genres()
        return genres if genres else None


@lru_cache()
def get_genre_service(
        genre_repository: GenreRepository = Depends(GenreRepository),
) -> GenreService:
    return GenreService(genre_repository)
