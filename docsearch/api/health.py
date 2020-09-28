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


class HealthCheckResource:
    def _start_indexing(self):
        try:
            job = Job.fetch(JOB_ID, connection=redis_client)
        except NoSuchJobError:
            if JOB_ID not in registry.get_job_ids():
                # There's no started or queued task, so reindex.
                queue.enqueue(index, job_id=JOB_ID,job_timeout=INDEXING_TIMEOUT)
                return

        if job.get_status() == JobStatus.FINISHED.value:
            # There's a finished indexing task but zero documents, so reindex.
            queue.enqueue(index, job_id=JOB_ID,job_timeout=INDEXING_TIMEOUT)

    def on_get(self, req, resp):
        """Make sure the search index is available."""
        try:
            info = search_client.info()
        except ResponseError as e:
            log.error("Health check failed: %s", e)
            self._start_indexing()
            resp.status = falcon.HTTP_503
            return

        if info['num_docs'] == 0:
            self._start_indexing()
            resp.status = falcon.HTTP_503
