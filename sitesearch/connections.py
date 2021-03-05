import os
import time

from dotenv import load_dotenv
from redis import Redis
from redisearch import Client, result

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_HOST = os.environ.get('REDIS_HOST')

ANALYTICS_REDIS_PASSWORD = os.environ.get('ANALYTICS_REDIS_PASSWORD')
ANALYTICS_REDIS_HOST = os.environ.get('ANALYTICS_REDIS_HOST')
ANALYTICS_REDIS_PORT = os.environ.get('ANALYTICS_REDIS_PORT')

load_dotenv()


class PipelinedSearchClient(Client):
    def make_result(self, query, res):
        st = time.time()
        return result.Result(res,
                not query._no_content,
                duration=(time.time() - st) * 1000.0,
                has_payload=query._with_payloads,
                with_scores=query._with_scores)

    def search(self, query, pipeline=None):
        """Search with a pipeline object if given one."""
        args, query = self._mk_query_args(query)
        client = pipeline if pipeline else self.redis
        res = client.execute_command(self.SEARCH_CMD, *args)

        if pipeline:
            return pipeline

        return self.make_result(query, res)

def get_redis_connection(password=REDIS_PASSWORD,
                         host=REDIS_HOST,
                         decode_responses=True):
    return Redis(password=password,
                 host=host,
                 decode_responses=decode_responses)


def get_search_connection(index: str,
                          password: str = REDIS_PASSWORD,
                          host: str = REDIS_HOST):
    conn = get_redis_connection(password=password, host=host)
    return PipelinedSearchClient(index, conn=conn)


def get_rq_redis_client():
    """The rq library expects to read raw strings."""
    return get_redis_connection(decode_responses=False)


def get_analytics_connection(password=ANALYTICS_REDIS_PASSWORD,
                             host=ANALYTICS_REDIS_HOST,
                             port=ANALYTICS_REDIS_PORT,
                             decode_responses=True):
    return Redis(password=password,
                 host=host,
                 port=port,
                 decode_responses=decode_responses)
