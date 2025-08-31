from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import PersonSearch, PersonDetail, FilmByPerson


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> PersonDetail | None:
        person = await self._get_person_from_elastic(person_id)
        if not person:
            return None
        return person

    async def get_search_list(self, query, page: int = 0,
                              page_size: int = 10) -> list[PersonSearch] | None:
        body = {
            "from": page * page_size,
            "size": page_size,
            "query": {
                "match": {
                    "full_name": query
                }
            }
        }
        persons = await self._get_list_persons_from_elastic(body)
        if not persons:
            return None
        return persons

    async def get_films_by_person(self, person_id: str) -> list[FilmByPerson] | None:
        films = await self._get_films_by_person_from_elastic(person_id)
        if not films:
            return None
        return films

    async def _get_person_from_elastic(self,
                                       person_id: str) -> PersonDetail | None:
        try:
            doc = await self.elastic.get(index='person', id=person_id)
        except NotFoundError:
            return None
        return PersonDetail(**doc['_source'])

    async def _get_list_persons_from_elastic(self,
                                             body: dict) -> list[PersonSearch] | None:
        try:
            doc = await self.elastic.search(index='person', body=body)
        except NotFoundError:
            return None
        return [PersonSearch(**obj['_source']) for obj in doc['hits']['hits']]

    async def _get_films_by_person_from_elastic(self,
                                                person_id: str) -> list[FilmByPerson] | None:
        try:
            # Ищем фильмы, где участвует данная персона в любой роли
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "actors",
                                    "query": {
                                        "term": {"actors.id": person_id}
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "directors",
                                    "query": {
                                        "term": {"directors.id": person_id}
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "writers",
                                    "query": {
                                        "term": {"writers.id": person_id}
                                    }
                                }
                            }
                        ]
                    }
                },
                "_source": ["id", "title", "imdb_rating"]
            }

            result = await self.elastic.search(index='movies', body=body)

            if not result['hits']['hits']:
                return None

            films = []
            for hit in result['hits']['hits']:
                films.append(FilmByPerson(
                    id=hit['_source']['id'],
                    title=hit['_source']['title'],
                    imdb_rating=hit['_source']['imdb_rating']
                ))

            return films

        except NotFoundError:
            return None


@lru_cache()
def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
