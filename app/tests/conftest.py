import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import asyncio
from elasticsearch import AsyncElasticsearch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture(scope="session")
def client():
    """Создание тестового клиента для FastAPI приложения"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def setup_test_data():
    """Настройка Elasticsearch и создание тестовых данных"""
    async def setup():
        es_host = os.getenv("ELASTIC_HOST_NAME", "localhost")
        es_port = "9200"
        es = AsyncElasticsearch(hosts=[f"http://{es_host}:{es_port}"])
        
        # Ждем пока Elasticsearch будет готов
        max_retries = 30
        for i in range(max_retries):
            try:
                await es.ping()
                break
            except Exception:
                if i == max_retries - 1:
                    raise Exception("Elasticsearch is not available")
                await asyncio.sleep(2)
        
        # Удаляем индекс если он существует
        if await es.indices.exists(index="movies"):
            await es.indices.delete(index="movies")
        
        # Создаем индекс movies
        await es.indices.create(index="movies")
        
        # Добавляем тестовый фильм
        film_uuid = str(uuid4())
        genre_uuid = str(uuid4())
        director_uuid = str(uuid4())
        actor_uuid = str(uuid4())
        writer_uuid = str(uuid4())
        
        test_film = {
            "id": film_uuid,
            "title": "Test Film",
            "description": "A test film for functional testing",
            "imdb_rating": 8.5,
            "genres": [
                {"id": genre_uuid, "name": "Test Genre"}
            ],
            "directors": [
                {"id": director_uuid, "name": "Test Director"}
            ],
            "actors": [
                {"id": actor_uuid, "name": "Test Actor"}
            ],
            "writers": [
                {"id": writer_uuid, "name": "Test Writer"}
            ]
        }
        
        # Добавляем второй фильм для тестов списка и поиска
        film_uuid2 = str(uuid4())
        test_film2 = {
            "id": film_uuid2,
            "title": "Another Test Movie",
            "description": "Another test film for testing list and search",
            "imdb_rating": 7.2,
            "genres": [
                {"id": genre_uuid, "name": "Test Genre"}
            ],
            "directors": [
                {"id": director_uuid, "name": "Test Director"}
            ],
            "actors": [
                {"id": actor_uuid, "name": "Test Actor"}
            ],
            "writers": [
                {"id": writer_uuid, "name": "Test Writer"}
            ]
        }
        
        await es.index(index="movies", id=film_uuid, body=test_film)
        await es.index(index="movies", id=film_uuid2, body=test_film2)
        await es.indices.refresh(index="movies")
        
        # Небольшая задержка для индексации
        await asyncio.sleep(2)
        
        await es.close()
        
        return film_uuid
    
    return asyncio.run(setup())