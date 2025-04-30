from functools import partial
from typing import Annotated

from app.controllers import cities
from app.dependencies.databases import AppDbDrivers
from app.dependencies.query_params import Pagination
from app.entities.city import City
from app.entities.responses import CollectionResponseModel, ResponseModel
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/cities", tags=["city"])


@router.get("/", summary="Get a paginated list of cities.")
def get_offers(
    drivers: Annotated[AppDbDrivers, Depends()],
    pagination: Annotated[Pagination, Depends()],
):
    return CollectionResponseModel(
        data=drivers.cached_query(
            partial(
                cities.get_cities_list,
                pagination=pagination,
            ),
            key=f"cities:{pagination.page}:{pagination.limit}",
            ttl=60,
        )
    )


@router.post("/", summary="Create a city")
def new_city(drivers: Annotated[AppDbDrivers, Depends()], city: City):
    return ResponseModel(data=cities.create_city(drivers, city))


@router.get(
    "/{city_code}",
    summary="Get a single city by its code.",
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
def get_single_city(
    drivers: Annotated[AppDbDrivers, Depends()],
    city_code: str,
) -> ResponseModel[City]:
    return ResponseModel(
        data=drivers.cached_query(
            partial(cities.get_city, city_code=city_code),
            key=f"cities:{city_code}",
            ttl=300,
        )
    )
