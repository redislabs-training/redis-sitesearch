import json
import logging
from collections import OrderedDict

import redis

from sitesearch.config import Config
from sitesearch.transformer import transform_documents
from sitesearch.connections import get_search_connection, get_redis_connection
from sitesearch.query_parser import parse
from .resource import Resource

config = Config()
redis_client = get_redis_connection()
log = logging.getLogger(__name__)

DEFAULT_NUM = 20
MAX_NUM = 100


class OrderedDefaultDict(OrderedDict):
    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        self[key] = value = self.factory()
        return value


class SearchResource(Resource):
    def on_get(self, req, resp):
        """Run a search."""
        query = req.get_param('q', default='')
        start = int(req.get_param('start', default=0))

        # TODO multi-site: decide which site to use based on query (header, URL?)
        search_site = config.default_search_site

        search_client = get_search_connection(search_site.index_name)

        try:
            num = min(int(req.get_param('num', default=DEFAULT_NUM)), MAX_NUM)
        except ValueError:
            num = DEFAULT_NUM

        q = parse(query, search_site).paging(start, num)

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
