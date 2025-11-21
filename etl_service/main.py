import time
from datetime import datetime
from typing import Generator, Any

import pytz
from dateutil import parser

from documents.movie import Movie, get_movie_index_data
from documents.person import Person, get_person_index_data
from documents.genre import Genre, get_genres_index_data
from logger import logger
from services.elasticsearch_service import ElasticsearchService
from services.elasticsearch_index_manager import ElasticsearchIndexManager
from state_manager.json_file_storage import JsonFileStorage
from state_manager.state_manager import StateManager
from settings import settings


def update_movie_index():
    """
    Обновить индекс фильмов в Elasticsearch с использованием новых сервисов.
    """
    # Инициализация сервисов
    es_service = ElasticsearchService()
    es_service.create_connection([settings.elasticsearch_settings.get_host()])
    
    index_manager = ElasticsearchIndexManager(es_service.get_connection())
    state_manager = StateManager(JsonFileStorage(logger=logger))

    # Получаем состояние синхронизации
    last_sync_state = state_manager.get_state('movie_index_last_sync_state')

    if last_sync_state is None:
        last_sync_state = pytz.UTC.localize(datetime.min)
    else:
        last_sync_state = parser.isoparse(last_sync_state)

    try:
        # Обеспечиваем существование индекса с правильными анализаторами
        index_manager.ensure_index_exists(Movie)
        
        # Загружаем и индексируем данные
        for rows in get_movie_index_data(settings.database_settings.get_dsn(), last_sync_state, 100):
            es_load_data = (dict(d.to_dict(True, skip_empty=False), **{'_id': d.id}) for d in rows)
            
            es_service.bulk_index(es_load_data)
            
            last_change_date = pytz.UTC.localize(max(item.last_change_date for item in rows))
            if last_change_date > last_sync_state:
                last_sync_state = last_change_date

        # Сохраняем состояние
        state_manager.set_state('movie_index_last_sync_state', last_sync_state.isoformat())
        logger.info("✅ Обновление индекса фильмов завершено успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении индекса фильмов: {e}")
        raise


def update_person_index():
    """
    Обновить индекс персон в Elasticsearch с использованием новых сервисов.
    """
    # Инициализация сервисов
    es_service = ElasticsearchService()
    es_service.create_connection([settings.elasticsearch_settings.get_host()])
    
    index_manager = ElasticsearchIndexManager(es_service.get_connection())
    state_manager = StateManager(JsonFileStorage(logger=logger))

    # Получаем состояние синхронизации
    last_sync_state = state_manager.get_state('person_index_last_sync_state')

    if last_sync_state is None:
        last_sync_state = pytz.UTC.localize(datetime.min)
    else:
        last_sync_state = parser.isoparse(last_sync_state)

    try:
        # Обеспечиваем существование индекса с правильными анализаторами
        index_manager.ensure_index_exists(Person)
        
        # Загружаем и индексируем данные
        for rows in get_person_index_data(settings.database_settings.get_dsn(), last_sync_state, 100):
            es_load_data = (dict(d.to_dict(True, skip_empty=False), **{'_id': d.id}) for d in rows)
            
            es_service.bulk_index(es_load_data)
            
            last_change_date = pytz.UTC.localize(max(item.last_change_date for item in rows))
            if last_change_date > last_sync_state:
                last_sync_state = last_change_date

        # Сохраняем состояние
        state_manager.set_state('person_index_last_sync_state', last_sync_state.isoformat())
        logger.info("✅ Обновление индекса персон завершено успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении индекса персон: {e}")
        raise


def update_genre_index():
    """
    Обновить индекс жанров в Elasticsearch с использованием новых сервисов.
    """
    # Инициализация сервисов
    es_service = ElasticsearchService()
    es_service.create_connection([settings.elasticsearch_settings.get_host()])
    
    index_manager = ElasticsearchIndexManager(es_service.get_connection())
    state_manager = StateManager(JsonFileStorage(logger=logger))

    # Получаем состояние синхронизации
    last_sync_state = state_manager.get_state('genre_index_last_sync_state')

    if last_sync_state is None:
        last_sync_state = pytz.UTC.localize(datetime.min)
    else:
        last_sync_state = parser.isoparse(last_sync_state)

    try:
        # Обеспечиваем существование индекса с правильными анализаторами
        index_manager.ensure_index_exists(Genre)
        
        # Загружаем и индексируем данные
        for rows in get_genres_index_data(settings.database_settings.get_dsn(), last_sync_state, 100):
            es_load_data = (dict(d.to_dict(True, skip_empty=False), **{'_id': d.id}) for d in rows)
            
            es_service.bulk_index(es_load_data)
            
            last_change_date = pytz.UTC.localize(max(item.last_change_date for item in rows))
            if last_change_date > last_sync_state:
                last_sync_state = last_change_date

        # Сохраняем состояние
        state_manager.set_state('genre_index_last_sync_state', last_sync_state.isoformat())
        logger.info("✅ Обновление индекса жанров завершено успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении индекса жанров: {e}")
        raise


if __name__ == '__main__':
    while True:
        try:
            update_movie_index()
            update_genre_index()
            update_person_index()
            time.sleep(60)
        except Exception as e:
            logger.exception(e)