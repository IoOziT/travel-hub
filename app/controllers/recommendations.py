from app.dependencies.databases import AppDbDrivers
from app.helpers.query import get_nearby_cities
from fastapi import HTTPException
from pydantic import PositiveInt


def get_recommendations(drivers: AppDbDrivers, *, city_code: str, limit: PositiveInt):
    exists_check_result = drivers.neo4j.execute_query(
        """
    MATCH (c:City { code: $city }) 
    RETURN c
    LIMIT 1;
    """,
        city=city_code,
    )

    city_exists = len(exists_check_result.records) > 0

    if not city_exists:
        raise HTTPException(404, "City not found")

    nearby_cities = get_nearby_cities(drivers.neo4j, city_code=city_code, limit=limit)

    recommended_offers = drivers.mongodb.offers.find(
        {"to": {"$in": [city.code for city in nearby_cities]}}
    ).to_list()

    return recommended_offers
