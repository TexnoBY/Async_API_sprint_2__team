from typing import Annotated, Union, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from http import HTTPStatus
from pydantic import BaseModel, Field
from src.services.film import FilmService, get_film_service
from src.services.person import PersonService, get_person_service
from src.services.genre import GenreService, get_genre_service
from src.models.film import FilmList
from src.models.person import PersonSearch
from src.models.genre import GenreList, Genre
from src.core.config import cache_service

router = APIRouter()


class SearchResult(BaseModel):
    """Модель для результата поиска"""
    type: str = Field(description="Тип сущности (film, person, genre)")
    data: Dict[str, Any] = Field(description="Данные найденной сущности")


class SearchResponse(BaseModel):
    """Модель для ответа поиска"""
    results: list[SearchResult] = Field(description="Список найденных результатов")
    total: int = Field(description="Общее количество найденных результатов")


@router.get('/search', response_model=SearchResponse)
@cache_service.cached(
    endpoint="api_search",
    params_extractor=lambda query, search_type, page_size, page_number, **kwargs: {
        "query": query,
        "search_type": search_type,
        "page_size": page_size,
        "page_number": page_number
    }
)
async def universal_search(
    query: Annotated[str, Query(description='Поисковый запрос')],
    search_type: Annotated[str, Query(description='Тип поиска: films, persons, genres, all')] = 'all',
    page_size: Annotated[int, Query(description='Размер страницы', ge=1)] = 10,
    page_number: Annotated[int, Query(description='Номер страницы', ge=0)] = 0,
    film_service: FilmService = Depends(get_film_service),
    person_service: PersonService = Depends(get_person_service),
    genre_service: GenreService = Depends(get_genre_service)
) -> SearchResponse:
    """
    Универсальный endpoint для поиска по фильмам, персонам и жанрам
    """
    results = []
    total = 0
    
    # Поиск по фильмам
    if search_type in ['films', 'all']:
        films = await film_service.get_search_list(query, page_number, page_size)
        if films:
            for film in films:
                results.append(SearchResult(type="film", data=film.model_dump()))
            total += len(films)
    
    # Поиск по персонам
    if search_type in ['persons', 'all']:
        persons = await person_service.get_search_list(query, page_number, page_size)
        if persons:
            for person in persons:
                results.append(SearchResult(type="person", data=person.model_dump()))
            total += len(persons)
    
    # Поиск по жанрам
    if search_type in ['genres', 'all']:
        genres = await genre_service.get_search_list(query, page_number, page_size)
        if genres:
            for genre in genres:
                results.append(SearchResult(type="genre", data=genre.model_dump()))
            total += len(genres)
    
    if not results:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='nothing found'
        )
    
    return SearchResponse(results=results, total=total)