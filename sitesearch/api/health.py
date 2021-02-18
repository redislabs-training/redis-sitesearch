import logging
from sitesearch import keys

from falcon.status_codes import HTTP_503
from redis.exceptions import ResponseError
from rq import Queue

from sitesearch.config import Config
from sitesearch.connections import get_search_connection, get_rq_redis_client
from .resource import Resource

config = Config()
redis_client = get_rq_redis_client()
search_client = get_search_connection(config.default_search_site.index_alias)
log = logging.getLogger(__name__)
queue = Queue(connection=redis_client)


class HealthCheckResource(Resource):
    def on_get(self, req, resp):
        """
        This service is considered unhealthy if:

        - The search index is unavailable
        - An indexing job is currently in progress

        If there is no index and an indexing job is not in progress,
        this check starts an indexing job in the background.
        """
        indexing_job_ids = redis_client.smembers(keys.startup_indexing_job_ids())

        if indexing_job_ids:
            # Indexing is in-progress, so the app shouldn't be available yet.
            resp.status = HTTP_503
            return

        try:
            search_client.info()
        except ResponseError as e:
            # The index doesn't exist -- this may indicate that indexing
            # hasn't started yet, or else our indexing tasks all failed.
            log.error("Response error: %s", e)
            resp.status = HTTP_503
