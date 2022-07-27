from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sitesearch.config import AppConfiguration
from sitesearch.api import search, indexer, health, job


def create_app(config=None):
    config = config or AppConfiguration()

    origins = [
        'https://developer.redis.com',
        'https://docs.redis.com',
        'https://docs.redislabs.com',
        'https://developer.redislabs.com',
        'http://localhost:3000',
        'http://localhost:1313',
        'http://localhost:8000',
        'http://docs-test.redislabs.com.s3-website-us-west-1.amazonaws.com',
        'https://docs-test.redislabs.com.s3-website-us-west-1.amazonaws.com',
        'https://docs-test.redislabs.com',
        'http://docs-test.redislabs.com',
        'https://redis.io',
        'https://kyle-buildout--redis-io.netlify.app'
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
