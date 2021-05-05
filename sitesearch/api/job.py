import json
import logging
import os

from falcon.errors import HTTPNotFound, HTTPUnauthorized
from rq.exceptions import NoSuchJobError
from rq.registry import StartedJobRegistry
from rq.serializers import JSONSerializer

from sitesearch import tasks
from sitesearch.connections import get_rq_redis_client
from sitesearch.cluster_aware_rq import ClusterAwareJob
from sitesearch.api.resource import Resource

redis_client = get_rq_redis_client()
log = logging.getLogger(__name__)
registry = StartedJobRegistry('default', connection=redis_client)

API_KEY = os.environ['API_KEY']
JOB_QUEUED = 'queued'


class JobResource(Resource):
    """Get indexing jobs."""
    def on_get(self, req, resp, job_id):
        """Get the status of a job by its ID."""
        token = req.get_header('Authorization')
        challenges = ['Token']

        if token is None:
            description = ('Please provide an auth token as part of the request.')
            raise HTTPUnauthorized('Auth token required', description, challenges)

        try:
            job = ClusterAwareJob.fetch(job_id, connection=redis_client)
        except NoSuchJobError as e:
            raise HTTPNotFound from e

        resp.body = json.dumps({
            "id": job_id,
            "url": job.args[0].url,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None
        })
