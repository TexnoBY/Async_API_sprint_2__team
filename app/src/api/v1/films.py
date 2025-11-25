from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import TypeAdapter
from src.api.v1.pagination import PaginationDep
from src.core.config import cache_service
from src.models.film import FilmList, FilmDitail
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/search', response_model=list[FilmList])
@cache_service.cached(
    endpoint="api_film_search",
    params_extractor=lambda query, pagination, **kwargs: {
        "query": query,
        "page_size": pagination.page_size,
        "page_number": pagination.page_number
    }
)
async def film_search(query: Annotated[str, Query(description='Word to search movie by title')],
                      pagination: PaginationDep,
                      film_service: FilmService = Depends(get_film_service)) -> list[FilmList]:
    films = await film_service.get_search_list(query, pagination.page_number, pagination.page_size)
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
                            detail='film not found')
    return film


@router.get('/', response_model=list[FilmList])
@cache_service.cached(
    endpoint="api_film_list",
    params_extractor=lambda pagination, sort, genres, **kwargs: {
        "sort": sort,
        "genres": genres,
        "page_size": pagination.page_size,
        "page_number": pagination.page_number
    }
)
async def film_list(pagination: PaginationDep,
                    sort: Annotated[str, Query(description='Field for sorting')] = '-imdb_rating',
                    genres: Annotated[str | None, Query(description='Genre ID to search')] = None,
                    film_service: FilmService = Depends(get_film_service)) -> list[FilmList]:
    if sort.startswith('-'):
        sort_order = 'desc'
        sort = sort[1:]
    else:
        sort_order = 'asc'
    films = await film_service.get_sort_list_by_param(sort, sort_order,
                                                      pagination.page_number,
                                                      pagination.page_size, genres or "")
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    adapter = TypeAdapter(list[FilmList])
    validated_list = adapter.validate_python(films)
    return validated_list
