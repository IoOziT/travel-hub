from functools import partial
from typing import Annotated, Optional, cast

from app.controllers import offers
from app.dependencies.databases import AppDbDrivers
from app.dependencies.query_params import Pagination
from app.entities.offer import Offer
from app.entities.responses import CollectionResponseModel, ResponseModel
from fastapi import APIRouter, Depends, Path, Query

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/", summary="Get a paginated list of offers.")
def get_offers(
    drivers: Annotated[AppDbDrivers, Depends()],
    pagination: Annotated[Pagination, Depends()],
    departure: Annotated[Optional[str], Query(min_length=3, alias="from")] = None,
    arrival: Annotated[Optional[str], Query(min_length=3, alias="to")] = None,
):
    return CollectionResponseModel[Offer](
        data=drivers.cached_query(
            partial(
                offers.get_offers_list,
                pagination=pagination,
                departure=departure,
                arrival=arrival,
            ),
            key=f"offers:{departure or "anywhere"}:{arrival or "anywhere"}:{pagination.page}:{pagination.limit}",
            ttl=60,
        )
    )


@router.post("/", summary="Create an offer")
def new_offer(drivers: Annotated[AppDbDrivers, Depends()], offer: Offer):
    created_offer = cast(Offer, offers.create_offer(drivers, offer))

    drivers.redis.publish("offers:new", created_offer.model_dump_json())

    return ResponseModel(data=created_offer)


@router.get(
    "/{id}",
    summary="Get a single offer by its ID.",
    responses={
        404: {
            "description": "City not found",
            "content": {
                "application/json": {
                    "example": {"detail": "City not found"},
                }
            },
        }
    },
)
def get_single_offer(
    offer_id: Annotated[str, Path(alias="id")],
    drivers: Annotated[AppDbDrivers, Depends()],
):
    return ResponseModel(
        data=drivers.cached_query(
            partial(offers.get_offer, offer_id=offer_id),
            key=f"offers:{offer_id}",
            ttl=300,
        )
    )
