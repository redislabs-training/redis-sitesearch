from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sitesearch.config import AppConfiguration
from sitesearch.api import search, indexer, health, job


def create_app(config=None):
    config = config or AppConfiguration()

    origins = [
        'https://docs.redislabs.com',
        'https://developer.redislabs.com',
        'http://localhost:3000',
        'http://localhost:1313',
        'http://localhost:8000',
    ]

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(search.router)
    app.include_router(indexer.router)
    app.include_router(health.router)
    app.include_router(job.router)

    return app
