import os

from dotenv import load_dotenv

load_dotenv()

from redisearch import Client

INDEX = "docs"


def get_redis_connection(password=os.environ['REDIS_PASSWORD'], host=os.environ['REDIS_HOST']):
    return Client(INDEX, password=password, host=host)
