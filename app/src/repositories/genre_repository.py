from typing import List, Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from src.models.genre import GenreList, GenreDitail, Genre
from src.services.interfaces import GenreRepositoryInterface
from src.core.database import elastic_factory


class GenreRepository(GenreRepositoryInterface):
    """Репозиторий для работы с жанрами"""
    
    def __init__(self, connection_factory=None):
        self.factory = connection_factory or elastic_factory
        self._client: Optional[AsyncElasticsearch] = None
    
    async def _get_client(self) -> AsyncElasticsearch:
        """Получает клиент Elasticsearch"""
        if self._client is None:
            self._client = await self.factory.get_connection()
        return self._client
    
    async def get_by_id(self, entity_id: str) -> Optional[GenreDitail]:
        try:
            client = await self._get_client()
            doc = await client.get(index='genres', id=entity_id)
            return GenreDitail(**doc['_source'])
        except NotFoundError:
            return None
    
    async def get_all(self) -> Optional[List[GenreList]]:
        body = {
            "query": {"match_all": {}},
            "size": 1000
        }
        try:
            client = await self._get_client()
            result = await client.search(index='genres', body=body)
            data = [hit['_source'] for hit in result['hits']['hits']]
            return [GenreList(**item) for item in data] if data else None
        except NotFoundError:
            return None
    
    async def search(self, query: str, page_number: int, page_size: int) -> Optional[List[Genre]]:
        """Поиск жанров по названию"""
        body = {
            "query": {
                "match": {
                    "name": {
                        "query": query,
                        "fuzziness": "auto"
                    }
                }
            },
            "from": page_number * page_size,
            "size": page_size
        }
        try:
            client = await self._get_client()
            result = await client.search(index='genres', body=body)
            data = [hit['_source'] for hit in result['hits']['hits']]
            return [Genre(**item) for item in data] if data else None
        except NotFoundError:
            return None