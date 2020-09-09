import json
import logging

import falcon
from falcon_cors import CORS

from docsearch.connections import get_redis_connection
from docsearch.query_parser import parse

client = get_redis_connection()
log = logging.getLogger(__name__)
cors = CORS(allow_origins_list=[
    'http://docs.andrewbrookins.com:1313',
    'http://localhost:8080']
)


class SearchResource:
    def on_get(self, req, resp):
        """Run a search."""
        # Dash postfixes confuse the query parser.
        query = req.get_param('q') or ''
        q = parse(query)
        res = client.search(q)

        resp.body = json.dumps({
            "total": res.total,
            "results": [{
                "title": doc.title,
                "section_title": doc.section_title,
                "root_page": doc.root_page,
                "parent_page": doc.parent_page,
                "body": doc.body,
                "url": doc.url
            } for doc in res.docs]
        })


api = falcon.API(middleware=[cors.middleware])
api.add_route('/search', SearchResource())
