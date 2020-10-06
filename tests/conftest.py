import os

import pytest
from falcon import testing

from sitesearch.api.app import create_app
from sitesearch.connections import get_redis_connection
from sitesearch.indexer import DocumentParser, Indexer
from sitesearch.sites.redis_labs import DOCS_STAGING


DOCS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "documents")
FILE_WITH_SECTIONS = "page_with_sections.html"
TEST_DOC = os.path.join(DOCS_DIR, FILE_WITH_SECTIONS)
TEST_URL = f"{DOCS_STAGING.url}/test"


@pytest.fixture(autouse=True)
def redis():
    redis_client = get_redis_connection()

    yield redis_client

    redis_client.flushdb()


@pytest.fixture
def client(scope="session"):
    yield testing.TestClient(create_app())


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

        return DocumentParser(
            DOCS_STAGING.validators).parse(TEST_URL, html)

    yield fn


@pytest.fixture
def docs(parse_file):
    indexer = Indexer(DOCS_STAGING)
    docs = parse_file(TEST_DOC)

    for doc in docs:
        indexer.index_document(doc)

    yield docs
