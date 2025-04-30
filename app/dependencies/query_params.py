from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, PositiveInt


class Pagination(BaseModel):
    page: Annotated[PositiveInt, Query(default=1)]
    limit: Annotated[PositiveInt, Query(default=10)]

    @property
    def offset(self):
        return (self.page - 1) * self.limit
