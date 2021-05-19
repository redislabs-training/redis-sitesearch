import logging

from fastapi import APIRouter, Security, status
from fastapi.exceptions import HTTPException
from rq.exceptions import NoSuchJobError
from rq.registry import StartedJobRegistry
from sitesearch.api.authentication import get_api_key
from sitesearch.cluster_aware_rq import ClusterAwareJob
from sitesearch.connections import get_rq_redis_client

redis_client = get_rq_redis_client()
log = logging.getLogger(__name__)
registry = StartedJobRegistry('default', connection=redis_client)
router = APIRouter()

JOB_QUEUED = 'queued'


@router.get("/jobs/{job_id}", dependencies=[Security(get_api_key)] )
async def job(job_id: str):
    """Get the status of a job by its ID."""
    try:
        job = ClusterAwareJob.fetch(job_id, connection=redis_client)
    except NoSuchJobError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Job not found") from e

    return {
        "id": job_id,
        "url": job.args[0].url,
        "status": job.get_status(),
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        "exc_info": job.exc_info
    }
