from typing import TypeVar, Generic

from src.services.film import FilmService
from src.services.genre import GenreService
from src.services.interfaces import FilmRepositoryInterface, GenreRepositoryInterface, PersonRepositoryInterface
from src.services.person import PersonService

T = TypeVar('T')


class ServiceFactory(Generic[T]):
    """Фабрика для создания сервисов"""

    @staticmethod
    def create_film_service(repository: FilmRepositoryInterface) -> FilmService:
        return FilmService(repository)

    @staticmethod
    def create_genre_service(repository: GenreRepositoryInterface) -> GenreService:
        return GenreService(repository)

    @staticmethod
    def create_person_service(repository: PersonRepositoryInterface) -> PersonService:
        return PersonService(repository)
