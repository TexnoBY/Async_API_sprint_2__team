from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

from src.core.cache_key_generator import CacheKeyGenerator
from src.core.cache_serializer import CacheSerializer
from src.core.cache_storage import CacheStorage
from src.core.logger import api_logger as logger


@dataclass
class CacheOptions:
    ttl: int = 300  # Время жизни кеша в секундах


class CacheService:
    def __init__(
            self,
            storage: CacheStorage,
            key_generator: CacheKeyGenerator,
            serializer: CacheSerializer = CacheSerializer()
    ):
        self.storage = storage
        self.key_generator = key_generator
        self.serializer = serializer

    async def get_cached_response(
            self,
            endpoint: str,
            params: dict[str, Any],
            fetch_func: Callable[[dict[str, Any]], Any],
            options: CacheOptions | None = None
    ) -> Any:
        """
        Получение кешированного ответа или выполнение и кеширование запроса

        :param endpoint: имя endpoint API
        :param params: параметры запроса
        :param fetch_func: функция для выполнения запроса к Elasticsearch
        :param options: настройки кеширования
        :return: результат запроса
        """
        options = options or CacheOptions()
        cache_key = await self.key_generator.generate_key(endpoint, params)

        try:
            cached_data = await self.storage.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return self.serializer.deserialize(cached_data)

            logger.debug(f"Cache miss for {cache_key}. Fetching data...")
            result = await fetch_func(params)

            await self.storage.set(
                cache_key,
                self.serializer.serialize(result),
                options.ttl
            )

            return result

        except Exception as e:
            logger.error(f"Error during cache operation: {str(e)}")
            raise

    def cached(
            self,
            endpoint: str | None = None,
            params_extractor: Callable[..., dict[str, Any]] | None = None,
            options: CacheOptions | None = None
    ):
        """

        :param endpoint: имя endpoint (если None, используется имя функции)
        :param params_extractor: функция для извлечения параметров из аргументов
        :param options: настройки кеширования
        """

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_options = options or CacheOptions()

                # Определяем endpoint
                actual_endpoint = endpoint or func.__name__

                # Извлекаем параметры
                if params_extractor:
                    params = params_extractor(*args, **kwargs)
                else:
                    # По умолчанию считаем, что все kwargs - это параметры
                    params = kwargs or (args[0] if args else {})

                cache_key = await self.key_generator.generate_key(actual_endpoint, params)

                # Попытка получить из кеша
                cached_data = await self.storage.get(cache_key)
                if cached_data is not None:
                    logger.info(f"Cache hit for {cache_key}")
                    return self.serializer.deserialize(cached_data)

                logger.info(f"Cache miss for {cache_key}. Fetching data...")
                result = await func(*args, **kwargs)

                await self.storage.set(
                    cache_key,
                    self.serializer.serialize(result),
                    cache_options.ttl
                )
                return result

            return wrapper

        return decorator

    async def invalidate_cache(self, endpoint: str, params: dict[str, Any]) -> None:
        """
        Инвалидация кеша для конкретного endpoint и параметров

        :param endpoint: имя endpoint API
        :param params: параметры запроса
        """
        cache_key = await self.key_generator.generate_key(endpoint, params)
        await self.storage.delete(cache_key)
        logger.debug(f"Cache invalidated for {cache_key}")

    async def clear_namespace(self, namespace: str) -> None:
        """
        Очистка всего кеша для указанного пространства имен

        :param namespace: пространство имен
        """
        pattern = f"{namespace}:*"
        await self.storage.clear_pattern(pattern)
        logger.info(f"Cleared cache namespace: {namespace}")
