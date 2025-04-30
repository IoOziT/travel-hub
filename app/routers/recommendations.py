from functools import partial
from typing import Annotated

from app.controllers import recommendations
from app.dependencies.databases import AppDbDrivers
from app.entities.offer import Offer
from app.entities.responses import CollectionResponseModel
from fastapi import APIRouter, Depends, Query
from pydantic import PositiveInt

router = APIRouter(tags=["recommendations"])


@router.get("/reco", summary="Get recommandations for a city")
async def get_recommandations(
    city: Annotated[str, Query(description="The 3-letter code of the city")],
    k: Annotated[
        PositiveInt, Query(description="The number of recommendations to return")
    ],
    drivers: Annotated[AppDbDrivers, Depends()],
):
    return CollectionResponseModel[Offer](
        data=drivers.cached_query(
            partial(recommendations.get_recommendations, city_code=city, limit=k),
            key=f"recommendations:{city}:{k}",
            ttl=3600,
        )
    )
