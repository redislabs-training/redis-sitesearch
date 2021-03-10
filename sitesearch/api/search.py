import json
import logging
from collections import OrderedDict

import falcon
import redis

from sitesearch.config import Config
from sitesearch.transformer import transform_documents
from sitesearch.connections import get_search_connection, get_redis_connection
from sitesearch.query_parser import parse
from sitesearch import indexer
from .resource import Resource

config = Config()
redis_client = get_redis_connection()
log = logging.getLogger(__name__)

DEFAULT_NUM = 30
MAX_NUM = 100


class SearchResource(Resource):
    def on_get(self, req, resp):
        """Run a search."""
        query = req.get_param('q', default='')
        from_url = req.get_param('from_url', default='')
        start = int(req.get_param('start', default=0))
        site_url = req.get_param('site', default=config.default_search_site.url)
        search_site = config.sites.get(site_url, config.default_search_site)
        section = indexer.get_section(site_url, from_url)

        if not search_site:
            raise falcon.HTTPBadRequest(
                "Invalid site", "You must specify a valid search site.")

        try:
            num = min(int(req.get_param('num', default=DEFAULT_NUM)), MAX_NUM)
        except ValueError:
            num = DEFAULT_NUM

        search_client = get_search_connection(search_site.index_alias)
        q = parse(query, section, search_site).paging(start, num)

        try:
            res = search_client.search(q)
        except (redis.exceptions.ResponseError, UnicodeDecodeError) as e:
            log.error("Search query failed: %s", e)
            total = 0
            docs = []
        else:
            docs = res.docs
            total = res.total

        docs = transform_documents(docs, search_site, q.query_string())

        resp.body = json.dumps({
            "total": total,
            "results": docs
        })
