import logging

from rq_scheduler import Scheduler

from docsearch.connections import get_rq_redis_client
from docsearch.indexer import Indexer


log = logging.getLogger(__name__)
redis_client = get_rq_redis_client()
scheduler = Scheduler(connection=redis_client)

JOB_ID = 'index'
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'
INDEXING_TIMEOUT = 60*15  # Fifteen minutes
SITES = ["https://docs.redislabs.com/"]  # TODO multi-site: store in redis


def index():
    for url in SITES:
        indexer = Indexer(url)
        indexer.index()
    return True


scheduler.cron(
    '0 */12 * * *',
    func=index,
)
