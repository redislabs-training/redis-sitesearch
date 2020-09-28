import json
import logging
import os

from falcon.errors import HTTPUnauthorized
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from rq.registry import StartedJobRegistry

from docsearch.connections import get_search_connection, get_rq_redis_client
from docsearch.tasks import JOB_ID, JOB_STARTED, JOB_NOT_QUEUED, index, INDEXING_TIMEOUT

redis_client = get_rq_redis_client()
search_client = get_search_connection()
log = logging.getLogger(__name__)
queue = Queue(connection=redis_client)
registry = StartedJobRegistry('default', connection=redis_client)

API_KEY = os.environ['API_KEY']


class IndexerResource:
    def on_get(self, req, resp):
        """Start an indexing job."""
        try:
            status = Job.fetch(JOB_ID, connection=redis_client).get_status()
        except NoSuchJobError:
            if JOB_ID in registry.get_job_ids():
                status = JOB_STARTED
            else:
                status = JOB_NOT_QUEUED

        resp.body = json.dumps({"job_id": JOB_ID, "status": status})

    def on_post(self, req, resp):
        """Start an indexing job."""
        token = req.get_header('Authorization')
        challenges = ['Token']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')
            raise HTTPUnauthorized('Auth token required', description, challenges)

        try:
            job = Job.fetch(JOB_ID, connection=redis_client)
        except NoSuchJobError:
            pass
        else:
            job.cancel()

        job = queue.enqueue(index, job_id=JOB_ID, job_timeout=INDEXING_TIMEOUT)

        resp.body = json.dumps({"job_id": JOB_ID, "status": job.get_status()})
