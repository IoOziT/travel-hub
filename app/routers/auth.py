from typing import Annotated
from uuid import uuid4

from app.dependencies.databases import get_redis_instance
from app.entities.auth import LoginInfo, Session
from app.entities.responses import ResponseModel
from fastapi import APIRouter, Depends
from redis import Redis

router = APIRouter(tags=["auth"])


@router.post("/login", summary="Creates a session")
def login(
    login_info: LoginInfo,
    redis: Annotated[Redis, Depends(get_redis_instance)],
):
    """
    Creates a session from an arbitrary user_id passed in the body.
    """

    uuid = uuid4()

    redis.set(f"session:{uuid}", login_info.user_id, ex=900)

    return ResponseModel(data=Session(token=uuid, expires_in=900))
