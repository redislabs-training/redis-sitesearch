
from sitesearch.keys import Keys
from sitesearch.config import AppConfiguration


class Resource:
    """A Falcon API that takes an AppConfiguration object."""
    def __init__(self, app_config: AppConfiguration):
        self.app_config = app_config
        self.keys = Keys(self.app_config.key_prefix)
