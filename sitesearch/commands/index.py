import logging

import click

from sitesearch import tasks
from sitesearch.config import Config


config = Config()
log = logging.getLogger(__name__)


@click.option('--create-index', default=False)
@click.command()
def index(create_index):
    """Index the app's configured sites in RediSearch."""
    tasks.index(config.sites, create_index=create_index)
