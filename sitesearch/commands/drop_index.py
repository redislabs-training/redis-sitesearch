import logging

import click

from sitesearch.connections import get_search_connection
from sitesearch.config import Config


config = Config()
log = logging.getLogger(__name__)


@click.argument('site')
@click.command()
def drop_index(site):
    """Index the app's configured sites in RediSearch."""
    site = config.sites.get(site)

    if site is None:
        valid_sites = ", ".join(config.sites.keys())
        raise click.BadArgumentUsage(
            f"The site you gave does not exist. Valid sites: {valid_sites}")

    redis_client = get_search_connection(site.index_name)
    redis_client.drop_index()
