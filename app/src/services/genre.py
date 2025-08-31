from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import GenreList, GenreDitail


class GenreService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> GenreDitail | None:
        genre = await self._get_genre_from_elastic(genre_id)
        if not genre:
            return None
        return genre

    async def get_all_genres(self) -> list[GenreList] | None:
        body = {
            "query": {
                "match_all": {}
            },
            "size": 1000  # Предполагаем, что жанров не очень много
        }
        genres = await self._get_list_genres_from_elastic(body)
        if not genres:
            return None
        return genres

    async def _get_genre_from_elastic(self,
                                      genre_id: str) -> GenreDitail | None:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return GenreDitail(**doc['_source'])

    async def _get_list_genres_from_elastic(self,
                                            body: dict) -> list[GenreList] | None:
        try:
            doc = await self.elastic.search(index='genres', body=body)
        except NotFoundError:
            return None
        return [GenreList(**obj['_source']) for obj in doc['hits']['hits']]


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
