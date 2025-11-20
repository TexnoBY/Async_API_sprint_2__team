from typing import Any, Dict, List, Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from src.repositories.base import BaseRepository
from src.core.database import elastic_factory


class ElasticsearchRepository(BaseRepository):
    """Реализация репозитория для Elasticsearch"""
    
    def __init__(self, connection_factory=None):
        self.factory = connection_factory or elastic_factory
        self._client: Optional[AsyncElasticsearch] = None
    
    async def _get_client(self) -> AsyncElasticsearch:
        """Получает клиент Elasticsearch"""
        if self._client is None:
            self._client = await self.factory.get_connection()
        return self._client
    
    async def get_by_id(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            client = await self._get_client()
            doc = await client.get(index=index, id=doc_id)
            return doc['_source']
        except NotFoundError:
            return None
    
    async def search(self, index: str, body: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            client = await self._get_client()
            result = await client.search(index=index, body=body)
            return [hit['_source'] for hit in result['hits']['hits']]
        except NotFoundError:
            return []
    
    async def exists(self, index: str, doc_id: str) -> bool:
        try:
            client = await self._get_client()
            return await client.exists(index=index, id=doc_id)
        except NotFoundError:
            return False