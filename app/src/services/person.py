from functools import lru_cache
from typing import List, Optional

from fastapi import Depends
from src.repositories.person_repository import PersonRepository
from src.models.person import PersonSearch, PersonDetail, FilmByPerson


class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.person_repo = person_repository

    async def get_by_id(self, person_id: str) -> Optional[PersonDetail]:
        return await self.person_repo.get_person_by_id(person_id)

    async def get_search_list(self, query: str, page: int = 0,
                              page_size: int = 10) -> Optional[List[PersonSearch]]:
        persons = await self.person_repo.search_persons(query, page, page_size)
        return persons if persons else None

    async def get_films_by_person(self, person_id: str) -> Optional[List[FilmByPerson]]:
        films = await self.person_repo.get_films_by_person(person_id)
        return films if films else None


@lru_cache()
def get_person_service(
        person_repository: PersonRepository = Depends(PersonRepository),
) -> PersonService:
    return PersonService(person_repository)
