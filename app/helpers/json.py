from datetime import date
from json import JSONEncoder

from bson import ObjectId
from pydantic import BaseModel


class JSONEncoder(JSONEncoder):
    def default(self, o):
        print(o, type(o))

        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, BaseModel):
            return o.model_dump_json()

        return super().default(o)
