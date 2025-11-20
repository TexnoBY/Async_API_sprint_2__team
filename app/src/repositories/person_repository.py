from typing import List, Optional
from src.repositories.elastic_repository import ElasticsearchRepository
from src.models.person import PersonSearch, PersonDetail, FilmByPerson


class PersonRepository(ElasticsearchRepository):
    """Репозиторий для работы с персонами"""
    
    async def get_person_by_id(self, person_id: str) -> Optional[PersonDetail]:
        data = await self.get_by_id('person', person_id)
        return PersonDetail(**data) if data else None
    
    async def search_persons(self, query: str, page: int, page_size: int) -> List[PersonSearch]:
        body = {
            "from": page * page_size,
            "size": page_size,
            "query": {"match": {"full_name": query}}
        }
        data = await self.search('person', body)
        return [PersonSearch(**item) for item in data]
    
    async def get_films_by_person(self, person_id: str) -> List[FilmByPerson]:
        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": person_id}}
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.id": person_id}}
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": person_id}}
                            }
                        }
                    ]
                }
            },
            "_source": ["id", "title", "imdb_rating"]
        }
        
        data = await self.search('movies', body)
        return [FilmByPerson(**item) for item in data]