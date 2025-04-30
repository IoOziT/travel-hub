from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt


class LoginInfo(BaseModel):
    user_id: Annotated[str, Field(alias="userId")]


class Session(BaseModel):
    token: UUID
    expires_in: PositiveInt
