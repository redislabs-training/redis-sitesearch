import logging

import click
from rq_scheduler.scheduler import Scheduler

from sitesearch.connections import get_rq_redis_client
from sitesearch import tasks
from sitesearch.config import Config


config = Config()
log = logging.getLogger(__name__)


@click.command()
def scheduler():
    """Run rq-scheduler"""
    redis_client = get_rq_redis_client()
    scheduler = Scheduler(connection=redis_client)

    # Create the RediSearch index and begin indexing immediately.
    # If a previous index exists, delete it.
    tasks.index(config.sites, rebuild_index=True, force=True)

    # Schedule an indexing job to run every 60 minutes.
    #
    # This performs an update-in-place using the existing RediSearch index.
    #
    # TODO: We currently don't try to detect if we have outdated content in
    # the index -- i.e. when we reindexed a site, a URL was leftover in the
    # index that we didn't find on this round of indexing.
    #
    # NOTE: We need to define this here, at the time we run this command,
    # because there is no deduplication in the cron() method, and this app has
    # no "exactly once" startup/initialization step that we could use to call
    # code only once.
    scheduler.cron(
        "*/60 * * * *",
        func=tasks.index,
        args=[config.sites, False],
        use_local_timezone=True,
        timeout=tasks.INDEXING_TIMEOUT
    )

    scheduler.run()
