import glob
import json
import logging
import sys

import falcon
from falcon_cors import CORS
import redis.exceptions
from redisearch import Client, Query

# Creating a client with a given index name
client = Client("docs")
log = logging.getLogger(__name__)
cors = CORS(allow_origins_list=['http://docs.andrewbrookins.com:1313'])


class SearchResource:
    def on_get(self, req, resp):
        """Run a search."""
        # Dash postfixes confuse the query parser.
        query = req.get_param('q').rstrip('-') or ''
        if query.endswith('-*'):
            query = f"{query[:-2]}*"

        q = Query(query).summarize('body', context_len=10).paging(0, 20)
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
