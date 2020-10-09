import logging
from typing import List

from rq_scheduler import Scheduler

from sitesearch.connections import get_rq_redis_client
from sitesearch.config import Config
from sitesearch.indexer import Indexer
from sitesearch.models import SiteConfiguration


config = Config()
log = logging.getLogger(__name__)
redis_client = get_rq_redis_client()
scheduler = Scheduler(connection=redis_client)

JOB_ID = 'index'
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'
INDEXING_TIMEOUT = 60*60  # One hour


def index(sites: List[SiteConfiguration], create_index=True):
    for site in sites:
        indexer = Indexer(site, create_index=create_index)
        indexer.index()
    return True


scheduler.cron(
    "*/42 * * * *",
    func=index,
    args=[config.sites, False],
    use_local_timezone=True
)
