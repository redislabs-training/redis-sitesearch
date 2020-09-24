import json
import logging
import os

import falcon
from rq import Queue

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch import tasks

redis_client = get_redis_connection()
search_client = get_search_connection()
log = logging.getLogger(__name__)
queue = Queue(connection=redis_client)

API_KEY = os.environ['API_KEY']
JOB_ID = 'index'
JOB_STARTED = 'started'
JOB_PENDING = 'pending'


class IndexerResource:
    def on_post(self, req, resp):
        """Start an indexing job."""
        token = req.get_header('Authorization')
        challenges = ['Token']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required', description, challenges)

        if JOB_ID in queue:
            status = JOB_PENDING
        else:
            queue.enqueue(tasks.index, job_id="index")
            status = JOB_STARTED

        resp.body = json.dumps({
            "job_id": JOB_ID,
            "status": status
        })
