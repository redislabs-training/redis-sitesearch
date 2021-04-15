import rq.registry
import rq.scheduler
import rq.suspension
import rq.worker_registration
import rq.contrib.legacy
from rq import Queue, Worker
from rq.job import Job
from rq_scheduler.scheduler import Scheduler

REDIS_QUEUE_NAMESPACE_PREFIX = '{rq}:queue:'
REDIS_QUEUE_KEYS = '{rq}:queue:queues'
REDIS_WORKER_KEY_REFIX = '{rq}:worker:'
REDIS_WORKER_KEYS = '{rq}:workers'
WORKERS_BY_QUEUE_KEY = '{rq}:workers:%s'
REDIS_JOB_PREFIX = '{rq}:job:'
REDIS_SCHEDULER_PREFIX = '{rq}:scheduler:scheduler_instance:'
REDIS_SCHEDULER_KEY = '{rq}:scheduler:scheduler'
REDIS_SCHEDULER_LOCK = '{rq}:scheduler:scheduler_lock'
REDIS_SCHEDULED_JOBS_KEY = '{rq}:scheduler:scheduled_jobs'

# RQ also includes a scheduler whose keys we need to monkey-patch.
# This schedule handled enqueue_at() -- NOT the cron-style schedule
# that rq-scheduler (which we also use) gives us.
RQ_SCHEDULER_KEY_TEMPLATE = '{rq}:rq-scheduler:%s'
RQ_SCHEDULER_LOCKING_KEY_TEMPLATE = '{rq}:rq-scheduler:scheduler-lock:%s'
rq.scheduler.SCHEDULER_KEY_TEMPLATE = RQ_SCHEDULER_KEY_TEMPLATE
rq.scheduler.SCHEDULER_LOCKING_KEY_TEMPLATE = RQ_SCHEDULER_LOCKING_KEY_TEMPLATE

# Monkey-patch key settings in this module -- no way to override!
rq.worker_registration.REDIS_WORKER_KEYS = REDIS_WORKER_KEYS
rq.worker_registration.WORKERS_BY_QUEUE_KEY = WORKERS_BY_QUEUE_KEY

# Monkey-patch registries which can't be overridden.
# I don't even care about constants at this point...
rq.registry.BaseRegistry.key_template = '{{rq}}:registry:{0}'
rq.registry.StartedJobRegistry.key_template = '{{rq}}:wip:{0}'
rq.registry.FailedJobRegistry.key_template = '{{rq}}:failed:{0}'
rq.registry.FinishedJobRegistry.key_template = '{{rq}}:finished:{0}'
rq.registry.DeferredJobRegistry.key_template = '{{rq}}:deferred:{0}'
rq.registry.ScheduledJobRegistry.key_template = '{{rq}}:scheduled:{0}'
rq.suspension.WORKERS_SUSPENDED = "{rq}:suspended"


class ClusterAwareJob(Job):
    """An RQ job whose keys support Redis Cluster"""
    redis_job_namespace_prefix = REDIS_JOB_PREFIX


class ClusterAwareQueue(Queue):
    """An RQ Queue whose keys work with Redis Cluster."""
    redis_queue_namespace_prefix = REDIS_QUEUE_NAMESPACE_PREFIX
    redis_queues_keys = REDIS_QUEUE_KEYS
    job_class = ClusterAwareJob

    @property
    def registry_cleaning_key(self):
        """Redis key used to indicate this queue has been cleaned."""
        return '{{rq}}:queue:clean_registries:%s' % self.name


class ClusterAwareWorker(Worker):
    """An RQ worker whose keys work with Redis Cluster."""
    redis_worker_namespace_prefix = REDIS_WORKER_KEY_REFIX
    redis_workers_keys = REDIS_WORKER_KEYS
    job_class = ClusterAwareJob


class ClusterAwareScheduler(Scheduler):
    """An RQ scheduler whose keys work with Redis Cluster."""
    redis_scheduler_namespace_prefix = REDIS_SCHEDULER_PREFIX
    scheduler_key = REDIS_SCHEDULER_KEY
    scheduler_lock_key = REDIS_SCHEDULER_LOCK
    scheduled_jobs_key = REDIS_SCHEDULED_JOBS_KEY
    queue_class = ClusterAwareQueue
    job_class = ClusterAwareJob


# Apparently the CLI calls the cleanup_ghosts() function in this module, which
# does not know anything about our custom worker class. Cool!
rq.contrib.legacy.Worker = ClusterAwareWorker
