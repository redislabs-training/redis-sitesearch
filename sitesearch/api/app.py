from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cprofile.profiler import CProfileMiddleware

from sitesearch.config import AppConfiguration
from sitesearch.api import search, indexer, health, job


config = AppConfiguration()

origins = [
    'https://docs.redislabs.com',
    'https://developer.redislabs.com',
    'http://localhost:3000',
    'http://localhost:1313',
    'http://localhost:8000',
]

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# ) 
# app.add_middleware(CProfileMiddleware, enable=True, print_each_request = True, strip_dirs = False, sort_by='tottime')

app.include_router(search.router)
app.include_router(indexer.router)
app.include_router(health.router)
app.include_router(job.router)
