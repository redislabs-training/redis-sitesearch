import json
import logging

import falcon
from falcon_cors import CORS
from rq import Queue

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch import tasks

redis_client = get_redis_connection()
search_client = get_search_connection()
log = logging.getLogger(__name__)
cors = CORS(allow_origins_list=[
    'http://docs.andrewbrookins.com:1313',
    'https://docs.redislabs.com',
    'http://localhost:8080']
)
queue = Queue(redis_client)


class IndexerResource:
    def on_put(self, req, resp):
        """Start an indexing job."""
        job = queue.enqueue(tasks.index)
        resp.body = json.dumps({
            "job_id": job.id,
            "status": job.get_status()
        })


api = falcon.API(middleware=[cors.middleware])
api.add_route('/indexer', IndexerResource())
