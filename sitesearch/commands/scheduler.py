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

    # We need to define this here, at the time we run this command, because
    # there is no deduplication in the cron() method, and this app has no
    # "exactly once" startup/initialization step that we could use to call
    # code only once.
    scheduler.cron(
        "*/30 * * * *",
        func=tasks.index,
        args=[config.sites, False],
        use_local_timezone=True
    )

    scheduler.run()
