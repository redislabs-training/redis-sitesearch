import click
from redisearch import Client, Query

from docsearch.connections import get_redis_connection

client = get_redis_connection()


@click.argument("query")
@click.command()
def search(query):
    # Dash postfixes confuse the query parser.
    query = query.rstrip('-*').rstrip('-') or ''
    q = Query(query).summarize('body', context_len=5).paging(0, 5)
    res = client.search(q)

    print(f"Hits: {res.total}")
    print()
    for doc in res.docs:
        print(f"{doc.root_page} - {doc.parent_page} - {doc.title}")
        if doc.section_title:
            print(f"[{doc.section_title}]")
        print(doc.body)
        print()
