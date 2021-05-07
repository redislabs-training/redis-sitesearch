import logging
import os

from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.security.api_key import APIKey
from rq.registry import StartedJobRegistry

from sitesearch import tasks
from sitesearch.api.authentication import get_api_key
from sitesearch.cluster_aware_rq import ClusterAwareQueue
from sitesearch.config import AppConfiguration, get_config
from sitesearch.connections import get_rq_redis_client

redis_client = get_rq_redis_client()
log = logging.getLogger(__name__)
queue = ClusterAwareQueue(connection=redis_client)
registry = StartedJobRegistry('default', connection=redis_client)
router = APIRouter()

API_KEY = os.environ['API_KEY']
JOB_QUEUED = 'queued'


@router.post("/indexer")
async def indexer(apiKey: APIKey = Depends(get_api_key),
                  config: AppConfiguration = Depends(get_config)):
    """Start indexing jobs for all configured sites."""
    jobs = []

    for site in config.sites.values():
        job = queue.enqueue(tasks.index,
                            args=[site],
                            kwargs={"force": True},
                            job_timeout=tasks.INDEXING_TIMEOUT)
        jobs.append(job.id)

    return {"jobs": jobs}
