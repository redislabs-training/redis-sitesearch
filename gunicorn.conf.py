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
worker_temp_dir = '/dev/shm'
reload = True

# https://docs.gunicorn.org/en/latest/faq.html#how-do-i-avoid-gunicorn-excessively-blocking-in-os-fchmod
worker_temp_dir = '/dev/shm'

worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 10000

# These settings only really help with sync and thread
# worker types, but let's configure them anyway.
workers = WORKERS
threads = WORKERS * 5
