from redisearch import Query


def parse(query):
    # Dash postfixes confuse the query parser.
    if query.endswith('-*'):
        query = f"{query[:-2]}*"
    query.replace('-', ' ')
    return Query(query).summarize('body', context_len=10).paging(0, 20)