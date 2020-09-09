import click

from docsearch.connections import get_redis_connection
from docsearch.query_parser import parse

client = get_redis_connection()


@click.argument("query")
@click.command()
def search(query):
    q = parse(query)
    res = client.search(q)

    print(f"Hits: {res.total}")
    print()
    for doc in res.docs:
        print(f"{doc.root_page} - {doc.parent_page} - {doc.title}")
        if doc.section_title:
            print(f"[{doc.section_title}]")
        print(doc.body)
        print()
