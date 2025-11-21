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
    # Устанавливаем переменные окружения для тестов
    os.environ.setdefault('ELASTIC_HOST_NAME', 'test_elastic_search')
    os.environ.setdefault('ELASTIC_PORT', '9200')
    os.environ.setdefault('REDIS_HOST', 'test_redis')
    os.environ.setdefault('REDIS_PORT', '6379')
    
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def test_settings():
    """Фикстура с тестовыми настройками"""
    from src.core.config import settings
    return settings


@pytest.fixture(scope="session")
def setup_test_data(test_settings):
    """Настройка Elasticsearch и создание тестовых данных"""
    async def setup():
        es = AsyncElasticsearch(hosts=[f"http://{test_settings.elastic_host}:{test_settings.elastic_port}"])
        
        # Ждем пока Elasticsearch будет готов
        max_retries = 30
        for i in range(max_retries):
            try:
                await es.ping()
                break
            except Exception as e:
                if i == max_retries - 1:
                    raise Exception(f"Elasticsearch is not available after {max_retries} attempts: {e}")
                await asyncio.sleep(2)
        
        # Очистка индексов перед тестами
        indices_to_clean = ["movies", "persons", "genres"]
        
        for index_name in indices_to_clean:
            if await es.indices.exists(index=index_name):
                await es.indices.delete(index=index_name)
        
        # Создаем индекс movies с тестовыми данными
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
        
        # Индексируем тестовые данные
        await es.index(index="movies", id=film_uuid, body=test_film)
        await es.index(index="movies", id=film_uuid2, body=test_film2)
        
        # Принудительное обновление индекса
        await es.indices.refresh(index="movies")
        
        # Проверяем, что данные успешно проиндексированы
        try:
            result = await es.get(index="movies", id=film_uuid)
            if not result['found']:
                raise Exception(f"Failed to index test film with UUID: {film_uuid}")
        except Exception as e:
            raise Exception(f"Test data verification failed: {e}")
        
        # Небольшая задержка для стабильности
        await asyncio.sleep(1)
        
        await es.close()
        
        return film_uuid
    
    return asyncio.run(setup())


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data(test_settings):
    """Очистка тестовых данных после всех тестов"""
    async def cleanup():
        es = AsyncElasticsearch(hosts=[f"http://{test_settings.elastic_host}:{test_settings.elastic_port}"])
        
        try:
            # Удаляем тестовые индексы
            indices_to_clean = ["movies", "persons", "genres"]
            for index_name in indices_to_clean:
                if await es.indices.exists(index=index_name):
                    await es.indices.delete(index=index_name)
        except Exception:
            # Игнорируем ошибки при очистке, так как это может нарушить CI/CD
            pass
        finally:
            await es.close()
    
    yield
    
    # Очистка после всех тестов
    asyncio.run(cleanup())