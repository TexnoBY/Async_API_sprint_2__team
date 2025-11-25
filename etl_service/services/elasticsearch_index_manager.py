from typing import Type

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document
from interfaces.index_manager_interface import IIndexManager
from logger import logger


class ElasticsearchIndexManager(IIndexManager):
    """
    Менеджер индексов Elasticsearch.
    Решает проблему с инициализацией анализаторов путем пересоздания индексов.
    """

    def __init__(self, elasticsearch_client: Elasticsearch):
        self.es = elasticsearch_client
        self.logger = logger

    def recreate_index_with_analyzers(self, document_class: Type) -> None:
        """
        Пересоздать индекс с правильными анализаторами.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
        """
        index_name = document_class.Index.name

        try:
            if self.es.indices.exists(index=index_name):
                self.logger.info(f"Удаляем существующий индекс: {index_name}")
                self.es.indices.delete(index=index_name)

            self.logger.info(f"Создаем индекс с анализаторами: {index_name}")
            document_class.init(using=self.es)

            settings = self.es.indices.get_settings(index=index_name)
            analysis = settings[index_name]['settings']['index'].get('analysis', {})

            if 'analyzer' in analysis and 'ru_en' in analysis['analyzer']:
                self.logger.info(f"✅ Анализатор ru_en успешно создан в индексе {index_name}")
            else:
                self.logger.warning(f"⚠️ Анализатор ru_en не найден в индексе {index_name}")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при пересоздании индекса {index_name}: {e}")
            raise

    def ensure_index_exists(self, document_class: Type) -> None:
        """
        Убедиться что индекс существует с правильными настройками.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
        """
        index_name = document_class.Index.name

        try:
            if not self.es.indices.exists(index=index_name):
                self.logger.info(f"Индекс {index_name} не существует, создаем...")
                document_class.init(using=self.es)
                return

            if self.index_needs_recreation(document_class):
                self.logger.info(f"Индекс {index_name} требует пересоздания для анализаторов")
                self.recreate_index_with_analyzers(document_class)
            else:
                self.logger.info(f"✅ Индекс {index_name} существует с правильными настройками")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке индекса {index_name}: {e}")
            raise

    def index_needs_recreation(self, document_class: Type) -> bool:
        """
        Проверить нужно ли пересоздавать индекс.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
            
        Returns:
            True если индекс нужно пересоздать, иначе False
        """
        index_name = document_class.Index.name

        try:
            current_settings = self._get_current_index_settings(index_name)

            expected_analysis = document_class.Index.settings.get('analysis', {})

            current_analysis = current_settings.get('analysis', {})

            if 'analyzer' not in current_analysis or 'ru_en' not in current_analysis['analyzer']:
                self.logger.info(f"Индекс {index_name}: отсутствует анализатор ru_en")
                return True

            current_ru_en = current_analysis['analyzer']['ru_en']
            expected_ru_en = expected_analysis['analyzer']['ru_en']

            if current_ru_en != expected_ru_en:
                self.logger.info(f"Индекс {index_name}: настройки анализатора ru_en отличаются")
                self.logger.debug(f"Текущие: {current_ru_en}")
                self.logger.debug(f"Ожидаемые: {expected_ru_en}")
                return True

            return False

        except Exception as e:
            self.logger.warning(f"Ошибка при проверке настроек индекса {index_name}: {e}")
            # В случае ошибки лучше пересоздать индекс для надежности
            return True

    def _get_current_index_settings(self, index_name: str) -> dict:
        """
        Получить текущие настройки индекса.
        
        Args:
            index_name: Имя индекса
            
        Returns:
            Словарь с настройками индекса
        """
        try:
            settings = self.es.indices.get_settings(index=index_name)
            return settings[index_name]['settings']['index']
        except Exception as e:
            self.logger.error(f"Ошибка получения настроек индекса {index_name}: {e}")
            return {}
