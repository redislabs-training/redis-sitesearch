import logging

import click

from docsearch import tasks


log = logging.getLogger(__name__)


@click.command()
def index():
    """Index the configured documentation site RediSearch."""
    tasks.index()
