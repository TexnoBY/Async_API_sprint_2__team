from typing import List, Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from src.services.interfaces import FilmRepositoryInterface
from src.models.film import FilmList, FilmDitail
from src.core.database import elastic_factory


class FilmRepository(FilmRepositoryInterface):
    """Репозиторий для работы с фильмами"""
    
    def __init__(self, connection_factory=None):
        self.factory = connection_factory or elastic_factory
        self._client: Optional[AsyncElasticsearch] = None
    
    async def _get_client(self) -> AsyncElasticsearch:
        """Получает клиент Elasticsearch"""
        if self._client is None:
            self._client = await self.factory.get_connection()
        return self._client
    
    async def get_by_id(self, entity_id: str) -> Optional[FilmDitail]:
        try:
            client = await self._get_client()
            doc = await client.get(index='movies', id=entity_id)
            return FilmDitail(**doc['_source'])
        except NotFoundError:
            return None
    
    async def search(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[FilmList]]:
        try:
            body = {
                "from": page * page_size,
                "size": page_size,
                "query": {"match": {"title": query}}
            }
            client = await self._get_client()
            result = await client.search(index='movies', body=body)
            return [FilmList(**hit['_source']) for hit in result['hits']['hits']]
        except NotFoundError:
            return []
    
    async def get_sorted(self, sort_field: str, sort_order: str = "asc",
                         page: int = 0, page_size: int = 10, **kwargs) -> Optional[List[FilmList]]:
        try:
            genres = kwargs.get('genres')
            body = {
                "sort": [{sort_field: {"order": sort_order}}],
                "from": page * page_size,
                "size": page_size,
            }
            if genres:
                body["query"] = {
                    'bool': {
                        'filter': [{
                            'nested': {
                                'path': 'genres',
                                'query': {'term': {'genres.id': str(genres)}}
                            }
                        }]
                    }
}
            client = await self._get_client()
            result = await client.search(index='movies', body=body)
            hits = result['hits']['hits']
            if not hits:
                return None
            return [FilmList(**hit['_source']) for hit in hits]
        except NotFoundError:
            return []