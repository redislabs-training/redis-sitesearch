import falcon
from falcon_cors import CORS

from sitesearch.config import AppConfiguration
from .search import SearchResource
from .indexer import IndexerResource
from .job import JobResource
from .health import HealthCheckResource


def create_app(config=None):
    config = config or AppConfiguration()

    cors = CORS(allow_origins_list=[
        'https://docs.redislabs.com',
        'https://developer.redislabs.com',
        'http://localhost:3000',
        'http://localhost:1313',
        'http://localhost:8000',
    ], allow_all_headers=True)

    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/search', SearchResource(config))
    api.add_route('/indexer', IndexerResource(config))
    api.add_route('/jobs/{job_id}', JobResource(config))
    api.add_route('/health', HealthCheckResource(config))

    return api
