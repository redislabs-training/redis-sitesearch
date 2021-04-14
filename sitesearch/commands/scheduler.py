import logging
from typing import Optional

import click
from redis import Redis
from rq_scheduler.scheduler import Scheduler

from sitesearch import tasks
from sitesearch.keys import Keys
from sitesearch.config import AppConfiguration
from sitesearch.connections import get_rq_redis_client
from sitesearch.cluster_aware_queue import ClusterAwareQueue

config = AppConfiguration()
log = logging.getLogger(__name__)


def schedule(scheduler: Scheduler, redis_client: Redis,
             config: Optional[AppConfiguration] = None):
    queue = ClusterAwareQueue(connection=redis_client)
    keys = Keys(prefix=config.key_prefix)

    for site in config.sites.values():
        job = queue.enqueue(tasks.index,
                            args=[site, config],
                            kwargs={
                                "force": True
                            },
                            job_timeout=tasks.INDEXING_TIMEOUT)

        # Track in-progress indexing tasks in a Redis set, so that we can
        # check if indexing is in-progress. Tasks should remove their
        # IDs from the set, so that when the set is empty, we think
        # indexing is done.
        redis_client.sadd(keys.startup_indexing_job_ids(), job.id)

        # Schedule an indexing job to run every 60 minutes.
        #
        # This performs an update-in-place using the existing RediSearch index.
        #
        # NOTE: We need to define this here, at the time we run this command,
        # because there is no deduplication in the cron() method, and this app has
        # no "exactly once" startup/initialization step that we could use to call
        # code only once.
        scheduler.cron(
            "*/60 * * * *",
            func=tasks.index,
            args=[site],
            kwargs={
                "force": False
            },
            use_local_timezone=True,
            timeout=tasks.INDEXING_TIMEOUT
        )

    redis_client.expire(keys.startup_indexing_job_ids(), tasks.INDEXING_TIMEOUT)


@click.command()
def scheduler():
    """Run rq-scheduler"""
    redis_client = get_rq_redis_client()
    scheduler = Scheduler(connection=redis_client)
    schedule(scheduler, redis_client, config)
    scheduler.run()
