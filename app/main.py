from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import films, genres, persons, search
from src.core.backoff import async_backoff
from src.core.config import settings
from src.core.logger import api_logger as logger
from src.db import elastic, redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    @async_backoff(0.1, 2, 10, logger)
    async def create_redis_connection():
        return Redis(host=settings.redis_host, port=settings.redis_port)
    
    @async_backoff(0.1, 2, 10, logger)
    async def create_elastic_connection():
        return AsyncElasticsearch(hosts=[f"http://{settings.elastic_host}"
                                         f":{settings.elastic_port}"])
    
    redis.redis = await create_redis_connection()
    elastic.es = await create_elastic_connection()
    yield
    await redis.redis.aclose()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


# Подключаем роутеры к серверу
# Теги указываем для удобства навигации по документации
app.include_router(films.router,
                   prefix='/api/v1/films',
                   tags=['films'])

app.include_router(genres.router,
                   prefix='/api/v1/genres',
                   tags=['genres'])

app.include_router(persons.router,
                    prefix='/api/v1/persons',
                    tags=['persons'])

app.include_router(search.router,
                    prefix='/api/v1',
                    tags=['search'])
