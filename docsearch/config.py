import os

from docsearch.sites.redis_labs import DOCS_PROD, DOCS_STAGING


class Config:
    def __init__(self):
        if os.environ.get('ENV') == 'development':
            self.sites = [DOCS_STAGING]
            self.default_search_site = DOCS_STAGING
            return

        self.sites = [DOCS_PROD]
        self.default_search_site = DOCS_PROD
