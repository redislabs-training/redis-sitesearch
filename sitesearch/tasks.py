import logging
from typing import List

from sitesearch.indexer import Indexer
from sitesearch.models import SiteConfiguration


log = logging.getLogger(__name__)

# These constants are used by other modules to refer to the
# state of the `index` task in the queueing/scheduling system.
JOB_ID = 'index'
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'
INDEXING_TIMEOUT = 60*60  # One hour


def index(sites: List[SiteConfiguration], rebuild_index=False, force=False):
    for site in sites:
        indexer = Indexer(site, rebuild_index=rebuild_index)
        indexer.index(force=force)
    return True
