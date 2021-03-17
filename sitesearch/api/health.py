import logging

import newrelic
from falcon.status_codes import HTTP_503
from redis.exceptions import ResponseError

from sitesearch import keys
from sitesearch.config import Config
from sitesearch.connections import get_search_connection, get_rq_redis_client
from .resource import Resource

config = Config()
search_client = get_search_connection(config.default_search_site.index_alias)
log = logging.getLogger(__name__)


class HealthCheckResource(Resource):
    def on_get(self, req, resp):
        """
        This service is considered unhealthy if the default search index is unavailable.
        """
        newrelic.agent.ignore_transaction(flag=True)
        try:
            search_client.redis.ping()
        except ResponseError as e:
            # Connection to Redis is probably down, so this node isn't healthy.
            log.error("Response error: %s", e)
            resp.status = HTTP_503
