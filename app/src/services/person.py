from typing import List, Optional

from src.services.base import SearchableService
from src.services.interfaces import PersonRepositoryInterface
from src.models.person import PersonSearch, PersonDetail, FilmByPerson


class PersonService(SearchableService):
    def __init__(self, person_repository: PersonRepositoryInterface):
        self._person_repo = person_repository

    async def get_by_id(self, person_id: str) -> Optional[PersonDetail]:
        return await self._person_repo.get_by_id(person_id)

    async def search(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[PersonSearch]]:
        persons = await self._person_repo.search(query, page, page_size)
        return persons if persons else None

    async def get_search_list(self, query: str, page: int = 0, page_size: int = 10) -> Optional[List[PersonSearch]]:
        return await self.search(query, page, page_size)

    async def get_films_by_person(self, person_id: str) -> Optional[List[FilmByPerson]]:
        films = await self._person_repo.get_films_by_person(person_id)
        return films


def get_person_service() -> PersonService:
    """Factory function for PersonService dependency injection"""
    from src.repositories.person_repository import PersonRepository
    from src.db.elastic import get_elastic_client
    
    # This is a simplified version - in real implementation you'd use proper DI
    elastic_client = get_elastic_client()
    person_repository = PersonRepository(elastic_client)
    return PersonService(person_repository)
