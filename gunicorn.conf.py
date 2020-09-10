import os
import multiprocessing
from dotenv import load_dotenv

load_dotenv()

PORT = os.environ['PORT']
WORKERS = multiprocessing.cpu_count() * 2 + 1


pidfile = '/tmp/hello-http-tcp.pid'
errorlog = '/tmp/gunicorn.log'
loglevel = 'warning'
bind = f':{PORT}'
daemon = False
workers = WORKERS
worker_class = 'gevent'
threads = 4