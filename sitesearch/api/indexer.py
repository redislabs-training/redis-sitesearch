import json
import logging
import os

from falcon.errors import HTTPUnauthorized
from rq.exceptions import NoSuchJobError
from rq.job import Job
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
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'


class IndexerResource(Resource):
    def on_get(self, req, resp):
        """Get job IDs for in-progress indexing tasks."""
        indexing_job_ids = redis_client.smembers(self.keys.startup_indexing_job_ids())
        jobs = []

        if indexing_job_ids:
            for job_id in indexing_job_ids:
                try:
                    status = Job.fetch(job_id, connection=redis_client).get_status()
                except NoSuchJobError:
                    if job_id in registry.get_job_ids():
                        status = JOB_STARTED
                    else:
                        status = JOB_NOT_QUEUED
                jobs.append({"job_id": job_id, "status": status})

        resp.body = json.dumps({"jobs": jobs})

    def on_post(self, req, resp):
        """Start an indexing job."""
        token = req.get_header('Authorization')
        challenges = ['Token']
        jobs = []

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')
            raise HTTPUnauthorized('Auth token required', description, challenges)

        indexing_job_ids = redis_client.smembers(self.keys.startup_indexing_job_ids())

        if indexing_job_ids:
            for job_id in indexing_job_ids:
                try:
                    job = Job.fetch(job_id, connection=redis_client)
                except NoSuchJobError:
                    pass
                else:
                    job.cancel()

        for site in self.app_config.sites.values():
            job = queue.enqueue(tasks.index,
                                args=[site],
                                kwargs={
                                    "force": True
                                },
                                job_timeout=tasks.INDEXING_TIMEOUT)
            redis_client.sadd(self.keys.startup_indexing_job_ids(), job.id)
            jobs.append({"job_id" :job.id, "status": "started"})

        resp.body = json.dumps({"jobs": jobs})
