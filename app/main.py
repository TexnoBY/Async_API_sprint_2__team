from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import films, genres, persons
from src.core.config import settings
from src.db import elastic, redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(hosts=[f"http://{settings.elastic_host}"
                                           f":{settings.elastic_port}"])
    yield
    await redis.redis.close()
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
