from typing import List, Optional
from src.repositories.elastic_repository import ElasticsearchRepository
from src.models.genre import GenreList, GenreDitail


class GenreRepository(ElasticsearchRepository):
    """Репозиторий для работы с жанрами"""
    
    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreDitail]:
        data = await self.get_by_id('genres', genre_id)
        return GenreDitail(**data) if data else None
    
    async def get_all_genres(self) -> List[GenreList]:
        body = {
            "query": {"match_all": {}},
            "size": 1000
        }
        data = await self.search('genres', body)
        return [GenreList(**item) for item in data]