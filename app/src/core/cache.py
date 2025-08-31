import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, date
from functools import wraps
from typing import Any, Callable
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio import Redis
from src.core.logger import api_logger as logger


@dataclass
class CacheOptions:
    ttl: int = 300  # Время жизни кеша в секундах


class CacheService:
    def __init__(self, redis_client: Redis, namespace: str = "api_cache"):
        """
            Инициализация сервиса кеширования

            :param redis_client: клиент Redis
            :param namespace: префикс для генерации кэша
        """
        self.redis = redis_client
        self.namespace = namespace

    async def _generate_cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        """
        Генерация ключа кеша на основе endpoint и параметров

        :param endpoint: имя endpoint API
        :param params: параметры запроса
        :return: сгенерированный ключ
        """
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{self.namespace}:{endpoint}:{param_hash}"

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
        cache_key = await self._generate_cache_key(endpoint, params)

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return json.loads(cached_data)

            logger.debug(f"Cache miss for {cache_key}. Fetching data...")
            result = await fetch_func(params)

            await self.redis.setex(cache_key,
                                   options.ttl,
                                   json.dumps(result, default=self._custom_serializer))

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

                cache_key = await self._generate_cache_key(actual_endpoint, params)

                # Попытка получить из кеша
                cached_data = await self.redis.get(cache_key)
                if cached_data is not None:
                    logger.info(f"Cache hit for {cache_key}")
                    return json.loads(cached_data)

                logger.info(f"Cache miss for {cache_key}. Fetching data...")
                result = await func(*args, **kwargs)

                await self.redis.setex(
                    cache_key,
                    cache_options.ttl,
                    json.dumps(result, default=self._custom_serializer)
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
        cache_key = await self._generate_cache_key(endpoint, params)

        await self.redis.delete(cache_key)
        logger.debug(f"Cache invalidated for {cache_key}")

    async def clear_namespace(self, namespace: str | None = None) -> None:
        """
        Очистка всего кеша для указанного пространства имен

        :param namespace: пространство имен (если None, используется основное)
        """
        namespace = namespace or self.namespace
        pattern = f"{namespace}:*"

        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)
        logger.info(f"Cleared cache namespace: {namespace}")

    def _custom_serializer(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
