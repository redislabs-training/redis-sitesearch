import logging

import falcon
from redis.exceptions import ResponseError
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus
from rq.registry import StartedJobRegistry

from docsearch.connections import get_search_connection, get_rq_redis_client
from docsearch.tasks import JOB_ID, INDEXING_TIMEOUT, index

redis_client = get_rq_redis_client()
search_client = get_search_connection()
log = logging.getLogger(__name__)
queue = Queue(connection=redis_client)
registry = StartedJobRegistry('default', connection=redis_client)

JOB_FINISHED_STATES = (
    JobStatus.FINISHED,
    JobStatus.FAILED
)
JOB_IN_PROGRESS_STATES = (
    JobStatus.QUEUED,
    JobStatus.STARTED
)


class HealthCheckResource:
    def on_get(self, req, resp):
        """
        This service is considered unhealthy if:

        - The search index is unavailable
        - An indexing job is currently in progress

        If there is no index and an indexing job is not in progress,
        this check starts an indexing job in the background.
        """
        try:
            status = Job.fetch(JOB_ID, connection=redis_client).get_status()
        except NoSuchJobError:
            # Indexing has started if our job is in this registry,
            # so we don't want to start it again, and the app
            # shouldn't be available yet.
            if JOB_ID in registry.get_job_ids():
                resp.status = falcon.HTTP_503
                return
            status = None

        if status in JOB_IN_PROGRESS_STATES:
            resp.status = falcon.HTTP_503
            return

        try:
            search_client.info()
        except ResponseError as e:
            log.error("Response error: %s", e)

            # We usually get a response error if the index doesn't exist.
            # If that's the case and we don't have an indexing job in
            # progress, we should try to reindex.
            resp.status = falcon.HTTP_503
            queue.enqueue(index, job_id=JOB_ID, job_timeout=INDEXING_TIMEOUT)
