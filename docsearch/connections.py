import os

from dotenv import load_dotenv
from redis import Redis
from redisearch import Client


INDEX = "docs"

load_dotenv()


def get_redis_connection(password=os.environ['REDIS_PASSWORD'], host=os.environ['REDIS_HOST'],
                         decode_responses=True):
    return Redis(password=password, host=host, decode_responses=decode_responses)


def get_search_connection(password=os.environ['REDIS_PASSWORD'], host=os.environ['REDIS_HOST']):
    conn = get_redis_connection()
    return Client(INDEX, conn=conn, password=password, host=host)


