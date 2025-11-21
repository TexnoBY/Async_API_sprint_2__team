from typing import List, Optional

from src.services.base import BaseService
from src.services.interfaces import GenreRepositoryInterface
from src.models.genre import GenreList, GenreDitail


class GenreService(BaseService):
    def __init__(self, genre_repository: GenreRepositoryInterface):
        self._genre_repo = genre_repository

    async def get_by_id(self, genre_id: str) -> Optional[GenreDitail]:
        return await self._genre_repo.get_by_id(genre_id)

    async def get_all_genres(self) -> Optional[List[GenreList]]:
        genres = await self._genre_repo.get_all()
        return genres if genres else None


def get_genre_service() -> GenreService:
    """Factory function for GenreService dependency injection"""
    from src.repositories.genre_repository import GenreRepository
    from src.db.elastic import get_elastic_client
    
    # This is a simplified version - in real implementation you'd use proper DI
    elastic_client = get_elastic_client()
    genre_repository = GenreRepository(elastic_client)
    return GenreService(genre_repository)
