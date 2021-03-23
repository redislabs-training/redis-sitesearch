import json
import logging
from sitesearch.commands.search import search

import falcon
import redis

from sitesearch.transformer import transform_documents
from sitesearch.connections import get_search_connection, get_redis_connection
from sitesearch.query_parser import parse
from sitesearch import indexer
from sitesearch.api.resource import Resource

redis_client = get_redis_connection()
log = logging.getLogger(__name__)

DEFAULT_NUM = 30
MAX_NUM = 100


class SearchResource(Resource):
    """The Sitesearch Search API.

    GET params:

        s: The search key. E.g. https://example.com/search?q=python

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
    def on_get(self, req, resp):
        """Run a search."""
        query = req.get_param('q', default='')
        from_url = req.get_param('from_url', default='')
        start = int(req.get_param('start', default=0))
        site_url = req.get_param(
            'site', default=self.app_config.default_search_site.url)
        search_site = self.app_config.sites.get(
            site_url, self.app_config.default_search_site)
        section = indexer.get_section(site_url, from_url)

        if not search_site:
            raise falcon.HTTPBadRequest(
                "Invalid site", "You must specify a valid search site.")

        try:
            num = min(int(req.get_param('num', default=DEFAULT_NUM)), MAX_NUM)
        except ValueError:
            num = DEFAULT_NUM

        index_alias = self.keys.index_alias(search_site.url)
        search_client = get_search_connection(index_alias)
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

        resp.body = json.dumps({"total": total, "results": docs})
