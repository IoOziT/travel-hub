from datetime import date
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import Field, PlainSerializer

PyObjectId = Annotated[
    Optional[str | ObjectId],
    Field(alias="_id", serialization_alias="id"),
    PlainSerializer(func=str, return_type=str, when_used="json-unless-none"),
]

MongoDate = Annotated[
    date,
    PlainSerializer(func=date.isoformat, return_type=str, when_used="json-unless-none"),
]
