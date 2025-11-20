from typing import Optional
from elasticsearch import AsyncElasticsearch
from src.core.config import settings


class ElasticsearchConnectionFactory:
    """Factory для создания Elasticsearch соединений"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._connection: Optional[AsyncElasticsearch] = None

    async def create_connection(self) -> AsyncElasticsearch:
        """Создает новое соединение с Elasticsearch"""
        return AsyncElasticsearch(
            hosts=[f"{self.host}:{self.port}"],
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )

    async def get_connection(self) -> AsyncElasticsearch:
        """Получает существующее или создает новое соединение"""
        if self._connection is None:
            self._connection = await self.create_connection()
        return self._connection

    async def close_connection(self) -> None:
        """Закрывает соединение"""
        if self._connection:
            await self._connection.close()
            self._connection = None


# Глобальный экземпляр factory
elastic_factory = ElasticsearchConnectionFactory(
    host=settings.elastic_host,
    port=settings.elastic_port
)