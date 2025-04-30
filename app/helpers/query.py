from app.entities.city import City
from neo4j import AsyncNeo4jDriver
from pydantic import PositiveInt


def get_nearby_cities(driver: AsyncNeo4jDriver, city_code: str, limit: PositiveInt):
    result = driver.execute_query(
        """
    MATCH (:City { code: $city })-[r:NEAR]-(c:City)
    RETURN c AS city
    ORDER BY r.weight DESC
    LIMIT $k;
    """,
        city=city_code,
        k=limit,
    )

    return [City(**record["city"]) for record in result.records]
