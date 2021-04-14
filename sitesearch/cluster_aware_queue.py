from rq import Queue


class ClusterAwareQueue(Queue):
    """An RQ Queue whose keys work with Redis Cluster."""
    redis_queue_namespace_prefix = 'rq:{queue}:queue:'
    redis_queues_keys = 'rq:{queue}:queues'
