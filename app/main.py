from contextlib import asynccontextmanager

from app.config import get_app_settings
from app.dependencies.databases import (
    AppDbDrivers,
    get_mongo_database,
    get_neo4j_driver,
    get_redis_instance,
)
from app.logger import logger
from app.routers import auth, cities, offers, recommendations
from app.seed import seed
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_settings = get_app_settings()

    logger.debug("App settings", app_settings)
    logger.debug("Connecting to databases...")

    mongodb = get_mongo_database(app_settings)
    redis = get_redis_instance(app_settings)
    neo4j = get_neo4j_driver(app_settings)

    logger.debug("Database connections established")

    drivers = AppDbDrivers(mongodb=mongodb, redis=redis, neo4j=neo4j)

    if app_settings.run_seed:
        seed(drivers)

    yield

    neo4j.close()
    mongodb.client.close()
    redis.close()


app = FastAPI(
    lifespan=lifespan,
    title="Sup de Vinci Travel Hub",
    summary="Plate-forme B2C qui aggrège vols, hébergements et activités touristiques afin de construire des itinéraires personnalisés quasi en temps réel.",
)

app.include_router(auth.router)
app.include_router(cities.router)
app.include_router(offers.router)
app.include_router(recommendations.router)
