import os

from dotenv import load_dotenv
from redis import Redis
from redisearch import Client

load_dotenv()

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)


def get_redis_connection(password=REDIS_PASSWORD,
                         host=REDIS_HOST,
                         port=REDIS_PORT,
                         decode_responses=True):
    return Redis(password=password,
                 host=host,
                 port=port,
                 decode_responses=decode_responses)


def get_search_connection(index: str,
                          password: str = REDIS_PASSWORD,
                          port=REDIS_PORT,
                          host: str = REDIS_HOST):
    conn = get_redis_connection(password=password, host=host, port=port)
    return Client(index, conn=conn)


def get_rq_redis_client():
    """The rq library expects to read raw strings."""
    return get_redis_connection(decode_responses=False)
