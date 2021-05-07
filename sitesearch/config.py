import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

from sitesearch import keys
from sitesearch.models import SiteConfiguration
from sitesearch.sites.redis_labs import CORPORATE, DOCS_PROD, DEVELOPERS, OSS, DOCS_STAGING
from sitesearch.sites.andrewbrookins import BLOG

load_dotenv()

DEFAULT_PREFIX = "sitesearch:test"
KEY_PREFIX = os.environ.get('KEY_PREFIX', DEFAULT_PREFIX)
ENV = os.environ.get('ENV')
IS_DEV = ENV in ('development', 'test')

# The front-end is currently querying with this URL. Temporarily allow it
# as an alternate for the configured URL.
ALTERNATE_DOCS_URL = "https://docs.redislabs.com/latest"

# Sites to index in development environments.
DEV_SITES = {
    DOCS_PROD.url: DOCS_PROD,
    ALTERNATE_DOCS_URL: DOCS_PROD,
    DEVELOPERS.url: DEVELOPERS,
    CORPORATE.url: CORPORATE,
    OSS.url: OSS,
    DOCS_STAGING.url: DOCS_STAGING,
    BLOG.url: BLOG  # Index Andrew's blog!
}

# Sites to index in production.
PROD_SITES = {
    DOCS_PROD.url: DOCS_PROD,
    ALTERNATE_DOCS_URL: DOCS_PROD,
    DEVELOPERS.url: DEVELOPERS,
}


# class AppConfiguration:
#     """Settings that apply globally to the entire app."""
#     def __init__(self,
#                  default_search_site: SiteConfiguration = DOCS_PROD,
#                  is_dev: bool = IS_DEV,
#                  key_prefix: str = KEY_PREFIX,
#                  env: str = ENV,
#                  sites: Optional[Dict[str, SiteConfiguration]] = DEV_SITES):

#         self.default_search_site = default_search_site
#         self.is_dev = is_dev
#         self.key_prefix = key_prefix
#         self.sites = sites
#         self.env = env
#         self.keys = keys.Keys(self.key_prefix)

#         if not IS_DEV:
#             self.sites = PROD_SITES


class AppConfiguration(BaseSettings):         
    default_search_site: SiteConfiguration = DOCS_PROD
    is_dev: bool = IS_DEV
    key_prefix: str = KEY_PREFIX
    env: str = ENV
    sites: Optional[Dict[str, SiteConfiguration]] = DEV_SITES
    keys: Optional['keys.Keys'] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)

        if not IS_DEV:
            self.sites = PROD_SITES

        self.keys = keys.Keys(self.key_prefix)


def get_config() -> AppConfiguration:
    return AppConfiguration()
