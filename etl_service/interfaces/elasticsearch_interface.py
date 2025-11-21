from abc import ABC, abstractmethod
from typing import Generator, Any
from elasticsearch import Elasticsearch


class IElasticsearchService(ABC):
    """
    Интерфейс для сервиса работы с Elasticsearch.
    Определяет контракт для соединений и операций с данными.
    """

    @abstractmethod
    def bulk_index(self, data: Generator[dict[str, Any], Any, None]) -> None:
        """
        Массовая индексация данных в Elasticsearch.
        
        Args:
            data: Генератор данных для индексации
        """
        pass

    @abstractmethod
    def get_connection(self) -> Elasticsearch:
        """
        Получить соединение с Elasticsearch.
        
        Returns:
            Экземпляр Elasticsearch клиента
        """
        pass

    @abstractmethod
    def create_connection(self, hosts: list[str]) -> Elasticsearch:
        """
        Создать соединение с Elasticsearch.
        
        Args:
            hosts: Список хостов Elasticsearch
            
        Returns:
            Экземпляр Elasticsearch клиента
        """
        pass