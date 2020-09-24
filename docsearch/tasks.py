import logging

from rq_scheduler import Scheduler

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.indexer import Indexer


log = logging.getLogger(__name__)
search_client = get_search_connection()
redis_client = get_redis_connection()
scheduler = Scheduler(connection=redis_client)


def index():
    indexer = Indexer(search_client)
    indexer.index()
    return True


scheduler.cron(
    '0 */12 * * *',
    func=index,
)
