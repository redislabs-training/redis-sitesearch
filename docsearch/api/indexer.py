import json
import logging

from rq import Queue

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch import tasks

redis_client = get_redis_connection()
search_client = get_search_connection()
log = logging.getLogger(__name__)
queue = Queue(connection=redis_client)


class IndexerResource:
    def on_post(self, req, resp):
        """Start an indexing job."""
        job = queue.enqueue(tasks.index)
        resp.body = json.dumps({
            "job_id": job.id,
            "status": job.get_status()
        })
