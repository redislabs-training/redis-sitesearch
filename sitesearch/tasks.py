import logging
from typing import Optional
from redis import ResponseError

from rq import get_current_job

from sitesearch.config import AppConfiguration
from sitesearch.connections import get_rq_redis_client, get_search_connection
from sitesearch.indexer import Indexer
from sitesearch.keys import Keys
from sitesearch.models import SiteConfiguration

log = logging.getLogger(__name__)

# These constants are used by other modules to refer to the
# state of the `index` task in the queueing/scheduling system.
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'
INDEXING_TIMEOUT = 60*60  # One hour


def index(site: SiteConfiguration, config: Optional[AppConfiguration] = None, force=False):
    redis_client = get_rq_redis_client()
    if config is None:
        config = AppConfiguration()
    indexer = Indexer(site, config)
    indexer.index(force)

    job = get_current_job()
    if job:
        keys = Keys(prefix=config.key_prefix)
        log.info("Removing indexing job ID: %s", job.id)
        redis_client.srem(keys.startup_indexing_job_ids(), job.id)

    return True


def clear_old_indexes(site: SiteConfiguration, config: Optional[AppConfiguration] = None):
    if config is None:
        config = AppConfiguration()
    keys = Keys(config.key_prefix)
    index_alias = keys.index_alias(site.url)
    redis_client = get_search_connection(index_alias)
    try:
        current_index = redis_client.info()['index_name']
    except ResponseError:
        log.info("Index alias does not exist: %s", index_alias)
        current_index = None

    old_indexes = [
        i for i in redis_client.redis.execute_command('FT._LIST')
        if i.startswith(index_alias) and i != current_index
    ]

    for idx in old_indexes:
        redis_client.redis.execute_command('FT.DROPINDEX', idx)

    return True
