import os
from typing import Dict, Optional

from dotenv import load_dotenv

from sitesearch.models import SiteConfiguration
from sitesearch.sites.redis_labs import CORPORATE, DOCS_PROD, DEVELOPERS, OSS, DOCS_STAGING
from sitesearch.sites.andrewbrookins import BLOG

load_dotenv()

DEFAULT_PREFIX = "sitesearch:test"
KEY_PREFIX = os.environ.get('KEY_PREFIX', DEFAULT_PREFIX)
ENV = os.environ.get('ENV')
IS_DEV = ENV in ('development', 'test')

# Sites to index in development environments.
DEV_SITES = {
    DOCS_PROD.url: DOCS_PROD,
    DEVELOPERS.url: DEVELOPERS,
    CORPORATE.url: CORPORATE,
    OSS.url: OSS,
    DOCS_STAGING.url: DOCS_STAGING,
    BLOG.url: BLOG  # Index Andrew's blog!
}

# Sites to index in production.
PROD_SITES = {
    DOCS_PROD.url: DOCS_PROD,
    DEVELOPERS.url: DEVELOPERS,
}


class AppConfiguration:
    """Settings that apply globally to the entire app."""
    def __init__(self,
                 default_search_site: SiteConfiguration = DOCS_PROD,
                 is_dev: bool = IS_DEV,
                 key_prefix: str = KEY_PREFIX,
                 env: str = ENV,
                 sites: Optional[Dict[str, SiteConfiguration]] = DEV_SITES):

        self.default_search_site = default_search_site
        self.is_dev = is_dev
        self.key_prefix = key_prefix
        self.sites = sites
        self.env = env

        if not IS_DEV:
            self.sites = PROD_SITES
