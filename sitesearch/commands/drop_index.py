import logging
from sitesearch.models import SiteConfiguration
from sitesearch.indexer import Indexer

import click
from redis.exceptions import ResponseError

from sitesearch.connections import get_search_connection
from sitesearch.config import AppConfiguration


log = logging.getLogger(__name__)


@click.argument('site')
@click.command()
def drop_index(site: SiteConfiguration, config: AppConfiguration):
    """Index the app's configured sites in RediSearch."""
    site = config.sites.get(site)
    if config is None:
        config = AppConfiguration()

    if site is None:
        valid_sites = ", ".join(config.sites.keys())
        raise click.BadArgumentUsage(
            f"The site you gave does not exist. Valid sites: {valid_sites}")

    redis_client = get_search_connection(site.index_alias)

    try:
        redis_client.execute_command('FT.DROPINDEX', site.index_alias)
    except ResponseError:
        log.info("Search index does not exist: %s", site.index_alias)

    indexer = Indexer(site, config)
    redis_client.redis.srem(indexer.index_name)
