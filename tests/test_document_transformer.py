import pytest

from redisearch import Document
from sitesearch.config import AppConfiguration
from sitesearch.models import TYPE_PAGE
from sitesearch.transformer import transform_documents


config = AppConfiguration()

@pytest.mark.asyncio
async def test_transform_documents_elides_body_if_longer_than_max():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], config.default_search_site, 'test', 5)

    assert docs[0]['body'] == "This ..."


@pytest.mark.asyncio
async def test_transform_documents_retains_body_if_shorter_than_max():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], config.default_search_site, 'test')

    assert docs[0]['body'] == "This is the body"


@pytest.mark.asyncio
async def test_transform_documents_decodes_hierarchy():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], config.default_search_site, 'test')

    assert docs[0]['hierarchy'] == ["one", "two"]


@pytest.mark.asyncio
async def test_transform_documents_raises_parse_error_with_bad_hierarchy():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='bad json',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], config.default_search_site, 'test')

    assert docs[0]['hierarchy'] == []


@pytest.mark.asyncio
async def test_transform_documents_injects_landing_page_doc():
    docs = transform_documents([], config.default_search_site, 'rc')
    assert docs[0]['title'] == 'Redis Enterprise Cloud'

    docs = transform_documents([], config.default_search_site, 'k8s*')
    assert docs[0]['title'] == 'Getting Started with Redis Enterprise Software using Kubernetes'


@pytest.mark.asyncio
async def test_transform_documents_unescapes_backslashes():
    doc = Document(
        id="123",
        title="Title\\-1",
        section_title="Section\\-1",
        hierarchy='["one", "two"]',
        url="http://example.com/1",
        body="This is the body\\-",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], config.default_search_site, 'test')

    assert docs[0]['title'] == "Title-1"
    assert docs[0]['section_title'] == "Section-1"
    assert docs[0]['body'] == "This is the body-"

