from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class City(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    code: Annotated[str, StringConstraints(min_length=3)]
    name: str
    country: Annotated[str, StringConstraints(min_length=2, max_length=3)]
