import logging

import click

from sitesearch import tasks
from sitesearch.config import Config

config = Config()


log = logging.getLogger(__name__)


@click.command()
def index():
    """Index the app's configured sites in RediSearch."""
    tasks.index(config.sites)
