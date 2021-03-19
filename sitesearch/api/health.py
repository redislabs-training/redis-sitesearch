import logging

from falcon.status_codes import HTTP_503
from redis.exceptions import ResponseError
from sitesearch.config import Config
from sitesearch.connections import get_search_connection
from .resource import Resource

config = Config()
search_client = get_search_connection(config.default_search_site.index_alias)
log = logging.getLogger(__name__)


class HealthCheckResource(Resource):
    def on_get(self, req, resp):
        """
        This service is considered unhealthy if the default search index is unavailable.
        """
        try:
            search_client.info()
        except ResponseError as e:
            # The index doesn't exist -- this may indicate that indexing
            # hasn't started yet, or else our indexing tasks all failed.
            log.error("Response error: %s", e)
            resp.status = HTTP_503
