import json
import logging
from typing import Optional

import redis
from fastapi import FastAPI, Query, HTTPException

from sitesearch.config import Config
from sitesearch.transformer import transform_documents
from sitesearch.connections import get_search_connection, get_redis_connection
from sitesearch.query_parser import parse
from sitesearch import indexer

config = Config()
redis_client = get_redis_connection()
log = logging.getLogger(__name__)
app = FastAPI()

DEFAULT_NUM = 30
MAX_NUM = 100


async def search(q: Optional[str] = Query(""),
                 from_url: Optional[str] = Query(""),
                 start: Optional[int] = Query(0),
                 num: Optional[int] = Query(DEFAULT_NUM),
                 site_url: Optional[str] = Query(config.default_search_site.url),
                 search_site: Optional[str] = Query(config.default_search_site)):
    search_site = config.sites.get(site_url, config.default_search_site)
    section = indexer.get_section(site_url, from_url)

    if not search_site:
        raise HTTPException(
            status_code=400, detail="You must specify a valid search site.")

    num = min(num, MAX_NUM)
    search_client = get_search_connection(search_site.index_alias)
    query = parse(q, section, search_site).paging(start, num)

    try:
        res = search_client.search(query)
    except (redis.exceptions.ResponseError, UnicodeDecodeError) as e:
        log.error("Search query failed: %s", e)
        total = 0
        docs = []
    else:
        docs = res.docs
        total = res.total

    docs = transform_documents(docs, search_site, q.query_string())

    return json.dumps({
        "total": total,
        "results": docs
    })
