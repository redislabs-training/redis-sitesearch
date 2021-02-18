import os

from dotenv import load_dotenv

from sitesearch.sites.redis_labs import CORPORATE, DOCS_PROD, DOCS_STAGING, DEVELOPERS, OSS

load_dotenv()

ENV = os.environ.get('ENV')
IS_DEV = ENV in ('development', 'test')


class Config:
    def __init__(self):
        if IS_DEV :
            self.sites = {
                DOCS_STAGING.url: DOCS_STAGING,
                DEVELOPERS.url: DEVELOPERS,
                CORPORATE.url: CORPORATE,
                OSS.url: OSS
            }
            self.default_search_site = DOCS_STAGING
            return

        self.sites = {
            DOCS_PROD.url: DOCS_PROD,
            DEVELOPERS.url: DEVELOPERS,
        }
        self.default_search_site = DOCS_PROD
        self.is_dev = IS_DEV
