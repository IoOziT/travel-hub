from typing import Annotated, Optional

from app.helpers.pydantic import MongoDate
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveFloat,
    PositiveInt,
    StringConstraints,
)

from .mongo import MongoModel


class TripLeg(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    flight_num: Annotated[str, Field(alias="flightNum")]
    dep: str
    arr: str
    duration: PositiveInt


class HotelStay(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    name: str
    nights: PositiveInt
    price: PositiveFloat


class Activity(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    title: str
    price: PositiveFloat


class Offer(MongoModel):
    from_: Annotated[str, Field(alias="from")]
    to: str
    depart_date: Annotated[MongoDate, Field(alias="departDate")]
    return_date: Annotated[MongoDate, Field(alias="returnDate")]
    provider: str
    price: PositiveFloat
    currency: Annotated[str, StringConstraints(min_length=2)]
    legs: list[TripLeg]
    hotel: Optional[HotelStay] = None
    activity: Optional[Activity] = None


class OfferWithRelatedOffers(Offer):
    related_offers: Annotated[list[Offer], Field(alias="relatedOffers")]
