import os

from dotenv import load_dotenv

from sitesearch.sites.redis_labs import DOCS_PROD, DOCS_STAGING

load_dotenv()

ENV = os.environ.get('ENV')
IS_DEV = ENV in ('development', 'test')


class Config:
    def __init__(self):
        if IS_DEV :
            self.sites = [DOCS_STAGING]
            self.default_search_site = DOCS_STAGING
            return

        self.sites = [DOCS_PROD]
        self.default_search_site = DOCS_PROD
