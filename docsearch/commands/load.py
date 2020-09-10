import glob
import sys


import click

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.indexer import Indexer


search_client = get_search_connection()
redis_client = get_redis_connection()
indexer = Indexer(search_client, redis_client)


@click.option(
    "-d",
    "--directory",
    help="A directory containing HTML files to load into the index",
    multiple=True)
@click.option(
    "-f",
    "--file",
    help="The path to an HTML file to load into the index",
    multiple=True)
@click.command()
def load(directory, file):
    all_files = []

    if not directory and not file:
        sys.exit("Error: please specify a file or directory to load")

    if directory:
        for _dir in directory:
            all_files += glob.glob(_dir + '/**/*.html', recursive=True)
    if file:
        all_files += file

    errors = indexer.index_files(all_files)

    if errors:
        print("Errors:")
        for error in errors:
            print(str(error))
