from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import TypeAdapter

from src.services.genre import GenreService, get_genre_service
from src.models.genre import GenreList, GenreDitail
from src.core.config import cache_service

router = APIRouter()


@router.get('/{genre_id}', response_model=GenreDitail)
@cache_service.cached(
    endpoint="api_genre_details",
    params_extractor=lambda genre_id, **kwargs: {"genre_id": genre_id}
)
async def genre_details(genre_id: Annotated[str, Path(description='Genre ID to display information')],
                        genre_service: GenreService = Depends(get_genre_service)) -> GenreDitail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return genre


@router.get('/', response_model=list[GenreList])
@cache_service.cached(
    endpoint="api_genre_list",
    params_extractor=lambda **kwargs: {}
)
async def genre_list(genre_service: GenreService = Depends(get_genre_service)) -> list[GenreList]:
    genres = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genres not found')
    adapter = TypeAdapter(list[GenreList])
    validated_list = adapter.validate_python(genres)
    return validated_list
