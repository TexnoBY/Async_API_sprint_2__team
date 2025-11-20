

from src.models.base import UUIDBase


class GenreList(UUIDBase):
    name: str


class GenreDitail(GenreList):
    description: str | None = None
