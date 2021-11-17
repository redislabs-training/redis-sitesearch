import re
from typing import List, Optional, Sequence

from sitesearch.models import SiteConfiguration

UNSAFE_CHARS = re.compile(r'[\[\]<>+]')


class TokenEscaper:
    """
    Escape literal tokens.

    A SiteConfiguration configures "literal tokens" that indexing and
    querying should special-case to support searching with punctuation.
    These are tokens like "active-active".

    This Escaper class takes a sequence of "literal tokens". When you call
    escape_string(), Escaper escapes punctuation within any literal tokens
    found in the input string.
    """

    ESCAPED_CHARS_RE = re.compile(r"[,.<>{}\[\]\\\"\':;!@#$%^&*()\-\+=~+]")

    def __init__(self, literal_terms: Sequence[str]):
        regex = "|".join(literal_terms)
        self.literal_terms_re = re.compile(f"{regex}", re.IGNORECASE)

    def escape(self, string):
        def escape_symbol(match):
            value = match.group(0)
            return f"\\{value}"

        def escape_string(match):
            value = match.group(0)
            return self.ESCAPED_CHARS_RE.sub(escape_symbol, value)

        return self.literal_terms_re.sub(escape_string, string)


async def parse(index_alias: str, query: str, section: Optional[str], start: int, num: int,
                search_site: SiteConfiguration) -> List[str]:

    # Dash postfixes confuse the query parser.
    query = query.strip().replace("-*", "*")
    query = UNSAFE_CHARS.sub(' ', query)
    query = query.strip()
    query = TokenEscaper(search_site.literal_terms).escape(query)

    # For queries of a term that should result in an exact match, e.g.
    # "insight" (a synonym of RedisInsight), or "active-active", strip any star
    # postfix to avoid the query becoming a prefix search.
    #
    # TODO: Why do we do this, again? Can we support prefix searches on
    #  queries with escaped tokens?
    if query.endswith('*'):
        exact_match_query = query.rstrip("*")
        if exact_match_query in search_site.all_synonyms:
            query = exact_match_query

    if query and section:
        # Boost results in the section the user is currently browsing.
        query = f"((@s:{section}) => {{$weight: 10}} {query}) | {query}"

    options = f'SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT {start} {num}'.split(' ')

    return [index_alias, query] + options
