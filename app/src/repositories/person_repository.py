from typing import List, Optional
from src.repositories.elastic_repository import ElasticsearchRepository
from src.models.person import PersonSearch, PersonDetail, FilmByPerson


class PersonRepository(ElasticsearchRepository):
    """Репозиторий для работы с персонами"""
    
    async def get_by_id(self, person_id: str) -> Optional[PersonDetail]:
        data = await super().get_by_id('persons', person_id)
        return PersonDetail(**data) if data else None
    
    async def search(self, query: str, page: int, page_size: int) -> List[PersonSearch]:
        body = {
            "from": page * page_size,
            "size": page_size,
            "query": {"match": {"full_name": query}}
        }
        data = await super().search('persons', body)
        return [PersonSearch(**item) for item in data]
    
    async def get_films_by_person(self, person_id: str) -> List[FilmByPerson]:
        body = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"actors_ids": person_id}},
                        {"term": {"directors_ids": person_id}},
                        {"term": {"writers_ids": person_id}}
                    ]
                }
            },
            "_source": ["id", "title", "imdb_rating"]
        }
        
        client = await self._get_client()
        result = await client.search(index='movies', body=body)
        data = [hit['_source'] for hit in result['hits']['hits']]
        return [FilmByPerson(**item) for item in data]