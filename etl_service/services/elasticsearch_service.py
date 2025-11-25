from typing import Generator, Any

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from helpers.backoff_func_wrapper import backoff
from interfaces.elasticsearch_interface import IElasticsearchService
from logger import logger


class ElasticsearchService(IElasticsearchService):
    """
    Сервис для работы с Elasticsearch.
    Управляет соединениями и операциями индексации.
    """

    def __init__(self):
        self._connection = None
        self.logger = logger

    @backoff(0.1, 2, 10, logger)
    def bulk_index(self, data: Generator[dict[str, Any], Any, None]) -> None:
        """
        Массовая индексация данных в Elasticsearch.
        
        Args:
            data: Генератор данных для индексации
        """
        try:
            bulk(
                self.get_connection(),
                data,
            )
            self.logger.info("✅ Данные успешно проиндексированы в Elasticsearch")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при индексации данных: {e}")
            raise

    def get_connection(self) -> Elasticsearch:
        """
        Получить соединение с Elasticsearch.
        
        Returns:
            Экземпляр Elasticsearch клиента
        """
        if self._connection is None:
            raise RuntimeError("Соединение не установлено. Вызовите create_connection()")
        return self._connection

    @backoff(0.1, 2, 10, logger)
    def create_connection(self, hosts: list[str]) -> Elasticsearch:
        """
        Создать соединение с Elasticsearch.
        
        Args:
            hosts: Список хостов Elasticsearch
            
        Returns:
            Экземпляр Elasticsearch клиента
        """
        self._connection = Elasticsearch(hosts=hosts)
        self.logger.info(f"✅ Соединение с Elasticsearch установлено: {hosts}")
        return self._connection
