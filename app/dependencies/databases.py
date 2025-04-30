import json
import zlib
from datetime import timedelta
from typing import Annotated, Callable, TypedDict, cast

from app.config import AppSettings, get_app_settings
from app.helpers.json import JSONEncoder
from fastapi import Depends, HTTPException
from neo4j import GraphDatabase, Neo4jDriver
from neo4j.exceptions import Neo4jError
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError
from redis import Redis, RedisError


class DriverCache(TypedDict):
    neo4j: GraphDatabase
    redis: Redis
    mongodb: Database


driver_cache = DriverCache()


def get_neo4j_driver(
    app_settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> Neo4jDriver:
    if "neo4j" in driver_cache and driver_cache["neo4j"] is not None:
        return driver_cache["neo4j"]

    try:
        driver = GraphDatabase.driver(
            str(app_settings.neo4j.uri),
            auth=(app_settings.neo4j.username, app_settings.neo4j.password),
            database="neo4j",
        )
        driver.verify_connectivity()
    except Neo4jError:
        driver.close()

        raise HTTPException(500, "Something went wrong, please try again later")
    else:
        driver_cache["neo4j"] = driver

        return driver_cache["neo4j"]


def get_mongo_database(
    app_settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> Database:
    if "mongodb" in driver_cache and driver_cache["mongodb"] is not None:
        return driver_cache["mongodb"]

    try:
        client = MongoClient(str(app_settings.mongodb.uri))
    except PyMongoError:
        raise HTTPException(500, "Something went wrong, please try again later")
    else:
        driver_cache["mongodb"] = client.sth

        return driver_cache["mongodb"]


def get_redis_instance(
    app_settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> Redis:
    if "redis" in driver_cache and driver_cache["redis"] is not None:
        return driver_cache["redis"]

    try:
        redis = Redis.from_url(str(app_settings.redis.uri), decode_responses=True)
    except RedisError:
        raise HTTPException(500, "Something went wrong, please try again later")
    else:
        driver_cache["redis"] = redis

        return driver_cache["redis"]


class AppDbDrivers:
    def __init__(
        self,
        mongodb: Annotated[Database, Depends(get_mongo_database)],
        redis: Annotated[Redis, Depends(get_redis_instance)],
        neo4j: Annotated[Neo4jDriver, Depends(get_neo4j_driver)],
    ):
        self.mongodb = mongodb
        self.redis = redis
        self.neo4j = neo4j

    def cached_query[R](
        self, query: Callable[["AppDbDrivers"], R], *, key: str, ttl: int | timedelta
    ) -> R:
        cache = cast(str, self.redis.get(key))

        if cache is not None:
            return json.loads(zlib.decompress(bytes.fromhex(cache)).decode())

        query_result = query(self)

        json_result = (
            query_result.model_dump_json()
            if isinstance(query_result, BaseModel)
            else json.dumps(query_result, cls=JSONEncoder)
        )

        self.redis.set(key, zlib.compress(json_result.encode()).hex(), ex=ttl)

        return query_result
