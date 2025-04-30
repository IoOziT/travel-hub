import random
from datetime import datetime, timedelta
from itertools import batched, islice
from typing import TypedDict, cast

import airportsdata
from app.dependencies.databases import AppDbDrivers
from app.entities.city import City
from app.entities.offer import Activity, HotelStay, Offer, TripLeg
from app.logger import logger
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorCollection
from neo4j import AsyncNeo4jDriver
from neo4j.graph import Node
from pydantic import PositiveInt

faker = Faker()


def airport_to_city(airport: airportsdata.Airport):
    return City(code=airport["iata"], name=airport["city"], country=airport["country"])


def city_to_node(city_entry: tuple[int, City]):
    index, city = city_entry

    return f"(c{index}:City {{ code: '{city.code}', name: '{city.name.replace("'", r"\'")}', country: '{city.country}' }})"


def airport_to_city_node(airport: airportsdata.Airport):
    return city_to_node(airport_to_city(airport))


def seed_cities(driver: AsyncNeo4jDriver):
    airports = airportsdata.load("IATA")

    driver.execute_query(
        """
    MATCH (c:City)
    DETACH DELETE c;
    """
    )

    for airport_batch in batched(airports.values(), 100):
        nodes = ", ".join(
            map(city_to_node, enumerate(map(airport_to_city, airport_batch)))
        )
        node_names = ", ".join(list(f"c{i}" for i in range(len(airport_batch))))

        query_result = driver.execute_query(
            f"CREATE {nodes} RETURN [{node_names}] AS nodes",
        )

        city_nodes = cast(list[Node], query_result.records[0]["nodes"])

        for city_node in city_nodes:
            yield City(**city_node)


def create_trip_legs(
    cities: list[City], departure: str, arrival: str, quantity: PositiveInt
):
    current_departure = departure
    legs: list[TripLeg] = []

    for _ in range(quantity - 1):
        leg_arrival = random.choice(cities).code

        while leg_arrival == arrival:
            leg_arrival = random.choice(cities).code

        legs.append(
            TripLeg(
                flightNum="000000",
                dep=current_departure,
                arr=leg_arrival,
                duration=timedelta(days=2).total_seconds(),
            )
        )

    legs.append(
        TripLeg(
            flightNum="000000",
            dep=current_departure,
            arr=arrival,
            duration=timedelta(days=2).total_seconds(),
        )
    )

    return legs


def create_offers(cities: list[City]):
    while True:
        departure, arrival = random.choices(cities, k=2)
        depart_date = faker.date_this_year(after_today=True)
        duration = timedelta(days=random.randint(1, 30))
        return_date = depart_date + duration
        price = faker.pyfloat(min_value=100, max_value=3000, right_digits=2)

        yield Offer.model_validate(
            {
                "from": departure.code,
                "to": arrival.code,
                "departDate": datetime.combine(depart_date, datetime.min.time()),
                "returnDate": datetime.combine(return_date, datetime.min.time()),
                "provider": faker.company(),
                "price": price,
                "currency": faker.currency_code(),
                "activity": (
                    None
                    if faker.boolean()
                    else Activity(
                        title=faker.bs(),
                        price=faker.pyfloat(
                            min_value=20, max_value=245, right_digits=2
                        ),
                    )
                ),
                "hotel": (
                    None
                    if faker.boolean()
                    else HotelStay(
                        name=faker.company(),
                        nights=duration.days,
                        price=faker.pyfloat(
                            min_value=100,
                            max_value=max(price * 0.75, 150),
                            right_digits=2,
                        ),
                    )
                ),
                "legs": create_trip_legs(
                    cities, departure.code, arrival.code, random.randint(0, 5)
                ),
            }
        ).model_dump()


def seed_offers(
    mongo_collection: AsyncIOMotorCollection, cities: list[City], quantity: int
):
    mongo_collection.delete_many({})

    for offer_batch in batched(islice(create_offers(cities), quantity), 100):
        result = mongo_collection.insert_many(offer_batch)
        offers = mongo_collection.find({"_id": {"$in": result.inserted_ids}}).to_list()

        for offer in offers:
            yield offer


class CityRelation(TypedDict):
    departure: str
    arrival: str
    weight: float


def generate_city_relations(cities: list[City]):
    for city in cities:
        for _ in range(3):
            neighbor = random.choice(cities)

            while neighbor is city:
                neighbor = random.choice(cities)

            yield CityRelation(
                departure=city.code, arrival=neighbor.code, weight=random.random()
            )


def seed_city_relation(drivers: AppDbDrivers, cities: list[City]):
    for relation_batch in batched(enumerate(generate_city_relations(cities)), 100):
        city_matches: list[str] = []
        relations: list[str] = []

        for index, relation in relation_batch:
            c1, c2 = f"c{index * 2}", f"c{index * 3}"
            city_matches.append(
                f"({c1}:City {{ code: '{ relation["departure"] }' }}), ({c2}:City {{ code: '{ relation["arrival"] }' }})"
            )

            relations.append(
                f"({c1})-[r{index}:NEAR {{ weight: { relation["weight"] } }}]->({c2})"
            )

        drivers.neo4j.execute_query(
            f"MATCH {', '.join(city_matches)} CREATE {', '.join(relations)}"
        )


def seed(drivers: AppDbDrivers):
    logger.debug("Starting cities seeding")

    cities = [city_batch for city_batch in seed_cities(drivers.neo4j)]

    logger.debug("Starting offers seeding")

    offers = [offer for offer in seed_offers(drivers.mongodb.offers, cities, 200)]

    logger.debug("Starting seeding of relations between cities")

    seed_city_relation(drivers, cities)

    logger.debug("Seeding done")

    return {"offers": offers, "cities": cities}
