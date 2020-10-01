import click
import logging
import redis

from docsearch.config import Config
from docsearch.transformer import transform_documents
from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.query_parser import parse

config = Config()
client = get_search_connection(config.default_search_site)
redis_client = get_redis_connection()
log = logging.getLogger(__name__)


@click.argument("query")
@click.command()
def search(query):
    q = parse(query, config.default_search_site.exact_matches)

    try:
        res = client.search(q)
    except redis.exceptions.ResponseError as e:
        log.error("Search query failed: %s", e)
        total = 0
        docs = []
    else:
        total = res.total
        docs = transform_documents(res.docs)

    print(f"Hits: {total}")
    print()
    for doc in docs:
        print(f"{doc['hierarchy']} - {doc['title']}")
        if doc['section_title']:
            print(f"[{doc['section_title']}]")
        print(doc['url'])
        print(doc['body'] or "NO BODY")
        print()
