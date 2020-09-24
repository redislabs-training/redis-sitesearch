import os
import multiprocessing
from dotenv import load_dotenv

load_dotenv()

PORT = os.environ['PORT']
WORKERS = multiprocessing.cpu_count() * 2 + 1


errorlog = "-"
accesslog = "-"
loglevel = 'warning'
bind = f':{PORT}'
daemon = False
workers = WORKERS
worker_class = 'gevent'
threads = 4
