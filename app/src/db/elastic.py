from src.core.database import elastic_factory


async def get_elastic():
    """Получение клиента Elasticsearch через factory"""
    return await elastic_factory.get_connection()


async def close_elastic():
    """Закрытие соединения с Elasticsearch"""
    await elastic_factory.close_connection()


def get_elastic_client():
    """Получение клиента Elasticsearch для dependency injection"""
    # This is a simplified version for testing
    # In real implementation, you'd return the actual client
    return None
