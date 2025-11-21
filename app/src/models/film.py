

from src.models.genre import GenreList
from src.models.person import PersonFilmDitail
from src.models.base import UUIDBase


class FilmList(UUIDBase):
    title: str
    imdb_rating: float
    genres: list[GenreList] = []
    directors: list[PersonFilmDitail] = []
    actors: list[PersonFilmDitail] = []
    writers: list[PersonFilmDitail] = []


class FilmDitail(FilmList):
    description: str | None = None
    genres: list[GenreList] = []
    directors: list[PersonFilmDitail] = []
    actors: list[PersonFilmDitail] = []
    writers: list[PersonFilmDitail] = []
