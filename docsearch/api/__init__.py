import falcon
from falcon_cors import CORS

from .search import SearchResource
from .indexer import IndexerResource

cors = CORS(allow_origins_list=[
    'http://docs.andrewbrookins.com:1313',
    'https://docs.redislabs.com',
    'http://localhost:8080',
    'http://localhost:1313'
])

api = falcon.API(middleware=[cors.middleware])
api.add_route('/search', SearchResource())
api.add_route('/indexer', IndexerResource())
