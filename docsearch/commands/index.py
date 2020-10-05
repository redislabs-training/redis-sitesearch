import logging

import click

from docsearch import tasks


log = logging.getLogger(__name__)


@click.argument('url')
@click.command()
def index(url):
    """Index the configured documentation site RediSearch."""
    tasks.index([url])
