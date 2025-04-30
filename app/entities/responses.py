from pydantic import BaseModel


class ResponseModel[T](BaseModel):
    data: T


class CollectionResponseModel[T](ResponseModel[list[T]]):
    pass
