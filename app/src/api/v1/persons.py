from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import TypeAdapter

from src.services.person import PersonService, get_person_service
from src.models.person import PersonSearch, PersonDetail, FilmByPerson
from src.core.config import cache_service

router = APIRouter()


@router.get('/search', response_model=list[PersonSearch])
@cache_service.cached(
    endpoint="api_person_search",
    params_extractor=lambda query, page_size, page_number, **kwargs: {
        "query": query,
        "page_size": page_size,
        "page_number": page_number
    }
)
async def person_search(query: Annotated[str, Query(description='Word to search person by name')],
                        page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
                        page_number: Annotated[int, Query(description='Pagination page number', ge=0)] = 0,
                        person_service: PersonService = Depends(get_person_service)) -> list[PersonSearch]:
    persons = await person_service.get_search_list(query, page_number, page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')
    adapter = TypeAdapter(list[PersonSearch])
    validated_list = adapter.validate_python(persons)
    return validated_list


@router.get('/{person_id}', response_model=PersonDetail)
@cache_service.cached(
    endpoint="api_person_details",
    params_extractor=lambda person_id, **kwargs: {"person_id": person_id}
)
async def person_details(person_id: Annotated[str, Path(description='Person ID to display information')],
                         person_service: PersonService = Depends(get_person_service)) -> PersonDetail:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return person


@router.get('/{person_id}/film', response_model=list[FilmByPerson])
@cache_service.cached(
    endpoint="api_person_films",
    params_extractor=lambda person_id, **kwargs: {"person_id": person_id}
)
async def person_films(person_id: Annotated[str, Path(description='Person ID to display information')],
                       person_service: PersonService = Depends(get_person_service)) -> list[FilmByPerson]:
    films = await person_service.get_films_by_person(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    adapter = TypeAdapter(list[FilmByPerson])
    validated_list = adapter.validate_python(films)
    return validated_list
