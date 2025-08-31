from functools import lru_cache
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import FilmList, FilmDitail


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> FilmDitail | None:
        film = await self._get_film_from_elastic(film_id)
        if not film:
            return None
        return film

    async def get_sort_list_by_param(self, sort_field: str,
                                     sort_order: str = "asc",
                                     page: int = 0, page_size: int = 10,
                                     genres: str = None) -> list[FilmList] | None:
        body = {
            "sort": [
                {sort_field: {"order": sort_order}}
            ],
            "from": page * page_size,
            "size": page_size,
        }
        if genres:
            body["query"] = {
                'bool': {
                    'filter': [
                        {
                            'nested': {
                                'path': 'genres',
                                'query': {
                                    'term': {'genres.id': str(genres)}
                                }
                            }
                        }
                    ]
                }
            }
        films = await self._get_list_films_from_elastic(body)
        if not films:
            return None
        return films

    async def get_search_list(self, query, page: int = 0,
                              page_size: int = 10) -> list[FilmList] | None:
        body = {
            "from": page * page_size,
            "size": page_size,
            "query": {
                "match": {
                    "title": query
                }
            }
        }
        films = await self._get_list_films_from_elastic(body)
        if not films:
            return None
        return films

    async def _get_film_from_elastic(self,
                                     film_id: str) -> FilmDitail | None:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return FilmDitail(**doc['_source'])

    async def _get_list_films_from_elastic(self,
                                           body: dict) -> list[FilmList] | None:
        try:
            doc = await self.elastic.search(index='movies', body=body)
        except NotFoundError:
            return None
        return [FilmList(**obj['_source']) for obj in doc['hits']['hits']]


@lru_cache()
def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
