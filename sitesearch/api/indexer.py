import json
import logging
import os

from falcon.errors import HTTPNotFound, HTTPUnauthorized
from rq.exceptions import NoSuchJobError
from rq.registry import StartedJobRegistry
from rq.serializers import JSONSerializer

from sitesearch import tasks
from sitesearch.connections import get_rq_redis_client
from sitesearch.cluster_aware_rq import ClusterAwareQueue, ClusterAwareJob
from sitesearch.api.resource import Resource

redis_client = get_rq_redis_client()
log = logging.getLogger(__name__)
queue = ClusterAwareQueue(connection=redis_client)
registry = StartedJobRegistry('default', connection=redis_client)

API_KEY = os.environ['API_KEY']
JOB_QUEUED = 'queued'


class IndexerResource(Resource):
    """Get and create indexing jobs."""
    def on_get(self, req, resp):
        """Get the status of a job by its ID."""
        token = req.get_header('Authorization')
        challenges = ['Token']
        job_id = req.get_param('id')

        if token is None:
            description = ('Please provide an auth token as part of the request.')
            raise HTTPUnauthorized('Auth token required', description, challenges)

        try:
            job = ClusterAwareJob.fetch(job_id, connection=redis_client, serializer=JSONSerializer)
        except NoSuchJobError as e:
            raise HTTPNotFound from e

        print(job.data)
        resp.body = job.data

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
