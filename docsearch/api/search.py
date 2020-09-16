import json
import logging
from collections import OrderedDict

import falcon
from falcon_cors import CORS

from docsearch.transformer import transform_documents
from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.query_parser import parse

search_client = get_search_connection()
redis_client = get_redis_connection()
log = logging.getLogger(__name__)
cors = CORS(allow_origins_list=[
    'http://docs.andrewbrookins.com:1313',
    'https://docs.redislabs.com',
    'http://localhost:8080']
)

DEFAULT_NUM = 10
MAX_NUM = 100


class OrderedDefaultDict(OrderedDict):
    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        self[key] = value = self.factory()
        return value


class SearchResource:
    def on_get(self, req, resp):
        """Run a search."""
        # Dash postfixes confuse the query parser.
        query = req.get_param('q', default='')
        start = int(req.get_param('start', default=0))

        try:
            num = min(int(req.get_param('num', default=DEFAULT_NUM)), MAX_NUM)
        except ValueError:
            num = DEFAULT_NUM

        q = parse(query).paging(start, num)
        res = search_client.search(q)
        docs = transform_documents(res.docs)

        resp.body = json.dumps({
            "total": res.total,
            "results": docs
        })


api = falcon.API(middleware=[cors.middleware])
api.add_route('/search', SearchResource())
