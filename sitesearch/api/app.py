import falcon
from falcon_cors import CORS

from sitesearch.config import Config
from .search import SearchResource
from .indexer import IndexerResource
from .health import HealthCheckResource


def create_app(config=None):
    config = config or Config()

    cors = CORS(allow_origins_list=[
        'https://docs.redislabs.com',
        'http://localhost:1313'
    ])

    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/search', SearchResource(config))
    api.add_route('/indexer', IndexerResource(config))
    api.add_route('/health', HealthCheckResource(config))

    return api
