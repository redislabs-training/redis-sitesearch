import logging
import time
from typing import Optional

import newrelic
import redis
from fastapi import APIRouter, Depends, HTTPException, status

from redisearch import Result
from sitesearch import indexer
from sitesearch.config import AppConfiguration, get_config
from sitesearch.connections import get_async_redis_connection
from sitesearch.query_parser import parse
from sitesearch.transformer import transform_documents

redis_client = get_async_redis_connection()
log = logging.getLogger(__name__)

DEFAULT_NUM = 30
MAX_NUM = 100

# Until we can get MINPREFIX set to 1 on Redis Cluster, map
# single-character queries to two-character queries. Use a
# static map so results are similar across queries.
SINGLE_CHAR_MAP = {
    'a': 'ac',
    'b': 'be',
    'c': 'co',
    'd': 'de',
    'e': 'en',
    'f': 'fi',
    'g': 'ge',
    'h': 'hi',
    'i': 'in',
    'j': 'ja',
    'k': 'ku',
    'l': 'lo',
    'm': 'ma',
    'n': 'ne',
    'o': 'of',
    'p': 'pe',
    'q': 'qu',
    'r': 'ra',
    's': 'se',
    't': 'ta',
    'u': 'us',
    'v': 'vo',
    'w': 'we',
    'x': '.x',
    'y': 'ya',
    'z': 'zo'
}

router = APIRouter()
config = get_config()


@router.get("/search")
async def search(q: str,
                 from_url: Optional[str] = None,
                 start: Optional[int] = None,
                 num: Optional[int] = None,
                 site: Optional[str] = None):
    """
    Make a full-text search against a site in the index.

    GET params:

        q: The search key. E.g. https://example.com/search?q=python

        from_url: The client's current URL. Including this param will
                  boost pages in the current section of the site based
                  on top-level hierarchy. E.g. https://example.com/search?q=python&from_url=https://example.com/technology
                  This query will boost documents whose URLs start with https://example.com/technology.

        start: For pagination. Controls the number of the document in the result
               to start with. Defaults to 0. E.g. https://example.com/search?q=python&start=20

        num: For pagination. Controls the number of documents to return, starting from
             `start`. https://example.com/search?q=python&start=20&num=20

        site_url: The site to search. Used when sitesearch is indexing multiple sites.
                  If this isn't specified, the query searches the default site specified in
                  AppConfiguration. E.g. https://example.com/search?q=python&site_url=https://docs.redislabs.com
    """
    from_url = from_url if from_url else ''
    start = start if isinstance(start, int) else 0
    num = num if isinstance(num, int) else DEFAULT_NUM
    site_url = site if site else config.default_search_site.url
    q_len = len(q)

    if q_len == 2 and q[1] == '*':
        char = q[0]
        if char in SINGLE_CHAR_MAP:
            q = f"{SINGLE_CHAR_MAP[q[0]]}*"

    # Return an error if a site URL was given but it's invalid.
    if site_url and site_url not in config.sites:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You must specify a valid search site.")

    search_site = config.sites.get(site_url)
    section = indexer.get_section(site_url, from_url)
    num = min(num, MAX_NUM)
    index_alias = config.keys.index_alias(search_site.url)
    query = await parse(index_alias, q, section, start, num, search_site)

    start = time.time()
    try:
        raw_result = await redis_client.execute_command("FT.SEARCH", *query)
    except (redis.exceptions.ResponseError, UnicodeDecodeError) as e:
        log.error("Search q failed: %s", e)
        total = 0
        docs = []
    else:
        result = Result(raw_result,
                        True,
                        duration=(time.time() - start) * 1000.0,
                        has_payload=False,
                        with_scores=False)
        total = result.total
        docs = result.docs
    end = time.time()
    newrelic.agent.record_custom_metric('search/q_ms', end - start)

    docs = await transform_documents(docs, search_site, q)
    return {"total": total, "results": docs}
