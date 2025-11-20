from src.core.database import elastic_factory


async def get_elastic():
    """Получение клиента Elasticsearch через factory"""
    return await elastic_factory.get_connection()


async def close_elastic():
    """Закрытие соединения с Elasticsearch"""
    await elastic_factory.close_connection()
