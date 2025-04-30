from app.helpers.pydantic import PyObjectId
from pydantic import BaseModel, ConfigDict


class MongoModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, serialize_by_alias=True, arbitrary_types_allowed=True
    )

    id: PyObjectId = None
