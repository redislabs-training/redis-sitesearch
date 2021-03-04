import re

from sitesearch.models import SiteConfiguration
from redisearch import Query

UNSAFE_CHARS = re.compile('[\\[\\]\\<\\>+]')


def parse(query: str, section: str, search_site: SiteConfiguration) -> Query:
    # Dash postfixes confuse the query parser.
    query = query.strip().replace("-*", "*")
    query = UNSAFE_CHARS.sub(' ', query)
    query = query.strip()

    # For queries of a term that should result in an exact match, e.g.
    # "insight" (a synonym of RedisInsight), or "active-active", strip any star
    # postfix to avoid the query becoming a prefix search.
    if query.endswith('*'):
        exact_match_query = query.rstrip("*")
        if exact_match_query in search_site.all_synonyms:
            query = exact_match_query

    if query and section:
        # Boost results in the section the user is currently browsing.
        query = f"((@s:{section}) => {{$weight: 10}} {query}) | {query}"

    return Query(query).summarize(
        'body', context_len=10, num_frags=1
    ).highlight(
        ('title', 'body', 'section_title')
    )
