from typing import List, Optional
from src.repositories.elastic_repository import ElasticsearchRepository
from src.models.film import FilmList, FilmDitail


class FilmRepository(ElasticsearchRepository):
    """Репозиторий для работы с фильмами"""
    
    async def get_film_by_id(self, film_id: str) -> Optional[FilmDitail]:
        data = await self.get_by_id('movies', film_id)
        return FilmDitail(**data) if data else None
    
    async def search_films(self, query: str, page: int, page_size: int) -> List[FilmList]:
        body = {
            "from": page * page_size,
            "size": page_size,
            "query": {"match": {"title": query}}
        }
        data = await self.search('movies', body)
        return [FilmList(**item) for item in data]
    
    async def get_sorted_films(self, sort_field: str, sort_order: str = "asc",
                              page: int = 0, page_size: int = 10,
                              genres: Optional[str] = None) -> List[FilmList]:
        body = {
            "sort": [{sort_field: {"order": sort_order}}],
            "from": page * page_size,
            "size": page_size,
        }
        if genres:
            body["query"] = {
                'bool': {
                    'filter': [{
                        'nested': {
                            'path': 'genres',
                            'query': {'term': {'genres.id': str(genres)}}
                        }
                    }]
                }
            }
        data = await self.search('movies', body)
        return [FilmList(**item) for item in data]