from abc import ABC, abstractmethod
from typing import Type


class IIndexManager(ABC):
    """
    Интерфейс для менеджера индексов Elasticsearch.
    Определяет контракт для управления созданием и обновлением индексов.
    """

    @abstractmethod
    def recreate_index_with_analyzers(self, document_class: Type) -> None:
        """
        Пересоздать индекс с правильными анализаторами.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
        """
        pass

    @abstractmethod
    def ensure_index_exists(self, document_class: Type) -> None:
        """
        Убедиться что индекс существует с правильными настройками.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
        """
        pass

    @abstractmethod
    def index_needs_recreation(self, document_class: Type) -> bool:
        """
        Проверить нужно ли пересоздавать индекс.
        
        Args:
            document_class: Класс документа Elasticsearch-dsl
            
        Returns:
            True если индекс нужно пересоздать, иначе False
        """
        pass
