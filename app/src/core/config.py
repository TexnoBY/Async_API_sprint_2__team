import os
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from redis.asyncio import Redis
from src.core.logger import LOGGING
from src.core.cache import CacheService

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    project_name: str = 'Some project name'
    redis_host: str = ...
    redis_port: int = ...
    elastic_host: str = Field(..., alias='ELASTIC_HOST_NAME')
    elastic_port: int = Field(9200, alias='ELASTIC_PORT')


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()

cache_service = CacheService(Redis(host=settings.redis_host, port=settings.redis_port))
