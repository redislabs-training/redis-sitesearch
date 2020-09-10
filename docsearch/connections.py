import os

from dotenv import load_dotenv
from redis import Redis
from redisearch import Client


INDEX = "docs"

load_dotenv()


def get_search_connection(password=os.environ['REDIS_PASSWORD'], host=os.environ['REDIS_HOST']):
    return Client(INDEX, password=password, host=host)


def get_redis_connection(password=os.environ['REDIS_PASSWORD'], host=os.environ['REDIS_HOST']):
    return Redis(password=password, host=host, decode_responses=True)
