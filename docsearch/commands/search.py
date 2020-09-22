import click

from docsearch.transformer import transform_documents
from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.query_parser import parse

client = get_search_connection()
redis_client = get_redis_connection()


@click.argument("query")
@click.command()
def search(query):
    q = parse(query)
    res = client.search(q)
    docs = transform_documents(res.docs)

    print(f"Hits: {res.total}")
    print()
    for doc in docs:
        print(f"{doc['hierarchy']} - {doc['title']}")
        if doc['section_title']:
            print(f"[{doc['section_title']}]")
        print(doc['url'])
        print(doc['body'] or "NO BODY")
        print()
