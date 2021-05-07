import logging

from fastapi import APIRouter, HTTPException, Response, status

from newrelic import agent
from redis.exceptions import ResponseError

from sitesearch.connections import get_redis_connection

redis_client = get_redis_connection()
log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    """This service is considered unhealthy if it can't ping Redis."""
    agent.ignore_transaction(flag=True)
    try:
        redis_client.ping()
    except ResponseError as e:
        # Connection to Redis is probably down, so this node isn't healthy.
        log.error("Response error: %s", e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Cannot reach Redis") from e
    return Response(status_code=status.HTTP_200_OK)
