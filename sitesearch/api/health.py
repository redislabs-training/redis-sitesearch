import logging

from falcon.status_codes import HTTP_503
from newrelic import agent
from redis.exceptions import ResponseError

from sitesearch.config import AppConfiguration
from sitesearch.connections import get_redis_connection
from .resource import Resource

config = AppConfiguration()
redis_client = get_redis_connection()
log = logging.getLogger(__name__)


class HealthCheckResource(Resource):
    def on_get(self, req, resp):
        """
        This service is considered unhealthy if the default search index is unavailable.
        """
        agent.ignore_transaction(flag=True)
        try:
            redis_client.ping()
        except ResponseError as e:
            # Connection to Redis is probably down, so this node isn't healthy.
            log.error("Response error: %s", e)
            resp.status = HTTP_503
