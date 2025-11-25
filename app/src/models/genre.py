from src.models.base import UUIDBase


class Genre(UUIDBase):
    name: str
    description: str | None = None


class GenreList(UUIDBase):
    name: str


class GenreDitail(GenreList):
    description: str | None = None
