from pydantic import Field
from src.models.base import UUIDBase


class PersonFilmDitail(UUIDBase):
    """Модель персоны для дитальной информации о фильме"""
    name: str


class PersonFilm(UUIDBase):
    """Модель фильма в контексте персоны"""
    roles: str


class PersonSearch(UUIDBase):
    """Модель для поиска персон"""
    full_name: str = Field(alias='name')
    films: list[PersonFilm]

    model_config = {
        "populate_by_name": True
    }


class PersonDetail(UUIDBase):
    """Модель детальной информации о персоне"""
    full_name: str = Field(alias='name')
    films: list[PersonFilm]

    model_config = {
        "populate_by_name": True
    }


class FilmByPerson(UUIDBase):
    """Модель фильма для эндпоинта фильмов по персоне"""
    title: str
    imdb_rating: float
