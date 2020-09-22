import logging

from docsearch.connections import get_search_connection
from docsearch.indexer import Indexer


log = logging.getLogger(__name__)
search_client = get_search_connection()


def index():
    indexer = Indexer(search_client)
    indexer.index()
    return True
