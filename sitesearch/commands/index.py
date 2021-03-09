import logging

import click

from sitesearch import tasks
from sitesearch.config import Config


config = Config()
log = logging.getLogger(__name__)


@click.argument('site')
@click.command()
def index(site):
    """Index the app's configured sites in RediSearch."""
    site = config.sites.get(site)

    if site is None:
        valid_sites = ", ".join(config.sites.keys())
        raise click.BadArgumentUsage(
            f"The site you gave does not exist. Valid sites: {valid_sites}")

    tasks.index(site, force=True)
