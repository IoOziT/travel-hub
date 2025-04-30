from functools import lru_cache
from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field, RedisDsn, UrlConstraints
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Neo4jDsn(AnyUrl):
    """A type that will accept any Neo4j DSN.

    * User info required
    * TLD not required
    * Host required (e.g., `neo4j+s://:pass@localhost`)
    """

    _constraints = UrlConstraints(
        allowed_schemes=["neo4j", "neo4j+s", "bolt", "bolt+s"],
        default_host="localhost",
    )


class Neo4JSettings(BaseModel):
    uri: Neo4jDsn
    username: str
    password: str


class RedisSettings(BaseModel):
    uri: RedisDsn


# Needed because pydantic's MongoDsn adds the port number and makes the url invalid
MongoSrvDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["mongodb+srv"])]


class MongoDBSettings(BaseModel):
    uri: MongoSrvDsn


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=".env", env_nested_delimiter="_"
    )

    run_seed: Annotated[bool, Field(alias="RUN_SEED")] = True
    neo4j: Neo4JSettings
    redis: RedisSettings
    mongodb: MongoDBSettings


@lru_cache
def get_app_settings():
    return AppSettings()
