import re
from redisearch import Query

UNSAFE_CHARS = re.compile('[\\[\\]\\-@+]')


def parse(query):
    # Dash postfixes confuse the query parser.
    query = query.strip().replace("-*", "*")
    query = UNSAFE_CHARS.sub(' ', query)
    return Query(query).summarize(
        'body', context_len=10
    ).highlight(
        ('title', 'body', 'section_title')
    ).paging(
        0, 15
    )
