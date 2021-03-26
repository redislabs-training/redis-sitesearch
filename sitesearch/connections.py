import os
import logging
import random
import time

from dotenv import load_dotenv
from redis import Redis, BusyLoadingError
from redisearch import Client

load_dotenv()

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
RETRY_COUNT = 3

log = logging.getLogger(__name__)


class RedisWrapper(Redis):
    """A wrapper around the Redis client class that retries on busy errors."""
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        # redis-py stores response callbacks on the __class__ function object
        if hasattr(attr, '__call__') and name != "__class__":
            def newfunc(*args, **kwargs):
                retries = 0
                while retries < RETRY_COUNT:
                    try:
                        result = attr(*args, **kwargs)
                    except BusyLoadingError:
                        sleep_seconds = random.randint(1, 5)
                        log.error("Redis is loading; sleeping for %s seconds [attempt %s]", sleep_seconds, retries)
                        time.sleep(sleep_seconds)
                        retries += 1
                    else:
                        break
                if retries == RETRY_COUNT:
                    log.error("Failed to connect to Redis - server is busy loading after %s retries", RETRY_COUNT)
                    raise BusyLoadingError
                return result
            return newfunc
        return attr


def get_redis_connection(password=REDIS_PASSWORD,
                         host=REDIS_HOST,
                         port=REDIS_PORT,
                         decode_responses=True):
    return RedisWrapper(password=password,
                        host=host,
                        port=port,
                        decode_responses=decode_responses,
                        retry_on_timeout=True)


def get_search_connection(index: str,
                          password: str = REDIS_PASSWORD,
                          port=REDIS_PORT,
                          host: str = REDIS_HOST):
    conn = get_redis_connection(password=password, host=host, port=port)
    return Client(index, conn=conn)


def get_rq_redis_client():
    """The rq library expects to read raw strings."""
    return get_redis_connection(decode_responses=False)
