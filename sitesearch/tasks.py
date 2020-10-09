import logging
from typing import List

from sitesearch.indexer import Indexer
from sitesearch.models import SiteConfiguration


log = logging.getLogger(__name__)

JOB_ID = 'index'
JOB_NOT_QUEUED = 'not_queued'
JOB_STARTED = 'started'
INDEXING_TIMEOUT = 60*60  # One hour


def index(sites: List[SiteConfiguration], create_index=True):
    for site in sites:
        indexer = Indexer(site, create_index=create_index)
        indexer.index()
    return True
