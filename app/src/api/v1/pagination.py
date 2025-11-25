from typing import Annotated

from fastapi import Depends, Query


class PaginationParams:
    def __init__(
        self,
        page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
        page_number: Annotated[int, Query(description='Pagination page number', ge=0)] = 0
    ):
        self.page_size = page_size
        self.page_number = page_number


PaginationDep = Annotated[PaginationParams, Depends()]