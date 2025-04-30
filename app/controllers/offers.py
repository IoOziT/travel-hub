from typing import Optional

from app.dependencies.databases import AppDbDrivers
from app.dependencies.query_params import Pagination
from app.entities.offer import Offer, OfferWithRelatedOffers
from app.helpers.query import get_nearby_cities
from bson.objectid import ObjectId
from fastapi import HTTPException


def get_offers_list(
    drivers: AppDbDrivers,
    *,
    pagination: Pagination,
    departure: Optional[str] = None,
    arrival: Optional[str] = None,
):
    return list(
        drivers.mongodb.offers.find(
            {"from": departure, "to": arrival},
            skip=pagination.offset,
            limit=pagination.limit,
        ).to_list()
    )


def get_offer(drivers: AppDbDrivers, *, offer_id: str):
    offer = drivers.mongodb.offers.find_one({"_id": ObjectId(offer_id)})

    if offer is None:
        raise HTTPException(404, "Offer not found")

    nearby_cities = get_nearby_cities(drivers.neo4j, offer["to"], 50)
    related_offers = drivers.mongodb.offers.find(
        {
            "to": {"$in": [nearby_city.code for nearby_city in nearby_cities]},
            "departDate": offer["departDate"],
        }
    )

    return OfferWithRelatedOffers(**offer, relatedOffers=related_offers)


def create_offer(drivers: AppDbDrivers, *, offer: Offer):
    offer_dict = offer.model_dump()

    drivers.mongodb.offers.insert_one(offer_dict)

    return Offer.model_validate(offer_dict)
