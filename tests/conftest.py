import os
import asyncio

import pytest
import aioredis
from httpx import AsyncClient
from sitesearch.api.app import create_app
from sitesearch.config import AppConfiguration
from sitesearch.connections import get_async_redis_connection
from sitesearch.indexer import DocumentParser, Indexer
from sitesearch.sites.redis_labs import DOCS_PROD

DOCS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "documents")
FILE_WITH_SECTIONS = "page_with_sections.html"
TEST_DOC = os.path.join(DOCS_DIR, FILE_WITH_SECTIONS)
TEST_URL = f"{DOCS_PROD.url}/test"


@pytest.fixture(autouse=True)
def redis():
    yield get_async_redis_connection()


@pytest.fixture(scope="function")
def app_config():
    yield AppConfiguration(key_prefix="sitesearch:test", env="test")


@pytest.fixture(scope="function")
async def client(app_config):
    async with AsyncClient(app=create_app(app_config), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def parse_file():
    """
    This fixture parses a file with DocumentParser.

    The fixture is a callable that takes the filename of a document
    and returns the SearchDocuments parsed from the HTML in the file.
    """
    def fn(filename):
        file = os.path.join(DOCS_DIR, filename)
        with open(file, encoding='utf-8') as f:
            html = f.read()

        return DocumentParser(DOCS_PROD.url, DOCS_PROD.validators,
                              DOCS_PROD.content_classes).parse(
                                  TEST_URL, html)

    yield fn


@pytest.fixture
def docs(parse_file, app_config):
    indexer = Indexer(DOCS_PROD, app_config)
    docs = parse_file(TEST_DOC)

    for doc in docs:
        indexer.index_document(doc)

    indexer.create_index_alias()

    yield docs


async def _delete_test_keys(prefix: str, conn: aioredis.Redis):
    async for key in conn.scan_iter(f"{prefix}:*"):
        await conn.delete(key)


@pytest.fixture(scope="function", autouse=True)
async def delete_test_keys(request, app_config):
    conn = get_async_redis_connection()
    await _delete_test_keys(app_config.key_prefix, conn)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
