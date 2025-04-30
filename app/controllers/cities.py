from app.dependencies.databases import AppDbDrivers
from app.dependencies.query_params import Pagination
from app.entities.city import City
from fastapi import HTTPException


def get_cities_list(drivers: AppDbDrivers, *, pagination: Pagination):
    query_result = drivers.neo4j.execute_query(
        f"MATCH (c:City) RETURN c AS city SKIP {pagination.offset} LIMIT {pagination.limit}"
    )

    return [City(**record["city"]) for record in query_result.records]


def get_city(drivers: AppDbDrivers, *, city_code: str):
    query_result = drivers.neo4j.execute_query(
        f"MATCH (c:City {{ code: '{city_code}' }}) RETURN c AS city LIMIT 1"
    )

    if len(query_result.records) == 0:
        raise HTTPException(404, "City not found")

    return City(**query_result.records[0]["city"])


def create_city(drivers: AppDbDrivers, *, city: City):
    result = drivers.neo4j.execute_query(
        f"CREATE (c:City {{ code: '{city.code}', country: '{ city.country }', name: '{ city.name.replace("'", r"\'") }' }})  RETURN c"
    )

    return City(**result.records[0]["city"])
