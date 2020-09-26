import os

REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
QUEUES = ['high', 'default', 'low']
