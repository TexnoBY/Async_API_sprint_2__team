from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from http import HTTPStatus
from pydantic import TypeAdapter
from src.models.film import FilmList, FilmDitail
from src.services.film import FilmService, get_film_service
from src.core.config import cache_service

router = APIRouter()


@router.get('/search', response_model=list[FilmList])
@cache_service.cached(
    endpoint="api_film_search",
    params_extractor=lambda query, page_size, page_number, **kwargs: {
        "query": query,
        "page_size": page_size,
        "page_number": page_number
    }
)
async def film_search(query: Annotated[str, Query(description='Word to search movie by title')],
                      page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
                      page_number: Annotated[int, Query(description='Pagination page number', ge=0)] = 0,
                      film_service: FilmService = Depends(get_film_service)) -> list[FilmList]:
    films = await film_service.get_search_list(query, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    adapter = TypeAdapter(list[FilmList])
    validated_list = adapter.validate_python(films)
    return validated_list


@router.get('/{film_id}', response_model=FilmDitail)
@cache_service.cached(
    endpoint="api_film_details",
    params_extractor=lambda film_id, **kwargs: {"film_id": film_id}
)
async def film_details(film_id: Annotated[str, Path(description='Movie ID to display information')],
                       film_service: FilmService = Depends(get_film_service)) -> FilmDitail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not founds')
    return film


@router.get('/', response_model=list[FilmList])
@cache_service.cached(
    endpoint="api_film_list",
    params_extractor=lambda sort, genres, page_size, page_number, **kwargs: {
        "sort": sort,
        "genres": genres,
        "page_size": page_size,
        "page_number": page_number
    }
)
async def film_list(sort: Annotated[str, Query(description='Field for sorting')] = '-imdb_rating',
                    genres: Annotated[str | None, Query(description='Genre ID to search')] = None,
                    page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
                    page_number: Annotated[int, Query(description='Pagination page number', ge=0)] = 0,
                    film_service: FilmService = Depends(get_film_service)) -> list[FilmList]:
    if sort.startswith('-'):
        sort_order = 'desc'
        sort = sort[1:]
    else:
        sort_order = 'asc'
    films = await film_service.get_sort_list_by_param(sort, sort_order,
                                                      page_number,
                                                      page_size, genres)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    adapter = TypeAdapter(list[FilmList])
    validated_list = adapter.validate_python(films)
    return validated_list
