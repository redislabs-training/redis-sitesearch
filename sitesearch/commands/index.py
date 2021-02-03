import logging

import click

from sitesearch import tasks
from sitesearch.config import Config


config = Config()
log = logging.getLogger(__name__)


@click.option('--rebuild-index', default=False)
@click.command()
def index(rebuild_index):
    """Index the app's configured sites in RediSearch."""
    tasks.index(config.sites, rebuild_index=rebuild_index, force=True)
