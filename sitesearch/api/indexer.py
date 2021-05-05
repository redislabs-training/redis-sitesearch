import json
import logging
import os

from falcon.errors import HTTPUnauthorized
from rq.registry import StartedJobRegistry

from sitesearch import tasks
from sitesearch.connections import get_rq_redis_client
from sitesearch.cluster_aware_rq import ClusterAwareQueue
from sitesearch.api.resource import Resource

redis_client = get_rq_redis_client()
log = logging.getLogger(__name__)
queue = ClusterAwareQueue(connection=redis_client)
registry = StartedJobRegistry('default', connection=redis_client)

API_KEY = os.environ['API_KEY']
JOB_QUEUED = 'queued'


class IndexerResource(Resource):
    """Start indexing jobs."""
    def on_post(self, req, resp):
        """Start indexing jobs for all configured sites."""
        token = req.get_header('Authorization')
        challenges = ['Token']
        jobs = []

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')
            raise HTTPUnauthorized('Auth token required', description, challenges)

        for site in self.app_config.sites.values():
            job = queue.enqueue(tasks.index,
                                args=[site],
                                kwargs={
                                    "force": True
                                },
                                job_timeout=tasks.INDEXING_TIMEOUT)
            jobs.append(job.id)

        resp.body = json.dumps({"jobs": jobs})
